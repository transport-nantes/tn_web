from random import randint
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.exceptions import ObjectDoesNotExist
# from django.shortcuts import render
from .models import TopicBlogPage, TopicBlogItem
from .forms import TopicBlogItemForm


class TopicBlogLegacyView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_slug = kwargs['topic_slug']
        # print('topic_slug=', topic_slug)
        # for page in TopicBlogPage.objects.all():
        #     print(page.id, ' - ', page.topic)
        try:
            page = TopicBlogPage.objects.random_topic_member(topic_slug)
        except:
            raise Http404("Page non trouvé (topic inconnu).")

        self.template_name = page.template
        context['page'] = page
        context['bullets'] = [
            [page.bullet_image_1, page.bullet_text_1_md],
            [page.bullet_image_2, page.bullet_text_2_md],
            [page.bullet_image_3, page.bullet_text_3_md],
            [page.bullet_image_4, page.bullet_text_4_md],
            [page.bullet_image_5, page.bullet_text_5_md],
            ]
        page.set_context(context)
        return context


# TOPICBLOG V2 ################################################################
class TopicBlogItemEdit(FormView):
    """Create a new TBItem or modify an existing one.

    It uses the fields of TopicBlogItem model to generate a form
    displayed inside the template set on template_name.
    The form exludes some fields that should not be accessible by the user.
    However admins can still edit those fields, for example the author.

    To create a new TopicBlogItem, the user must go on the url
    /tb/admin/new where the form is displayed with empty fields.

    If an existing item doesn't have a slug yet, it's possible to edit it
    by going to /tb/admin/edit/<PKid> however if it does already have a slug
    then you must also provide the slug to edit it.
    For example :
    /tb/admin/edit/15/la-grande-mobilite/ would return a 200 status code
    if the item with PK 15 has the slug la-grande-mobilite.
    However it would return a 404 status code you try to edit it from
    /tb/admin/edit/15/.

    It's possible to edit an item by its slug, the form will load the
    instance of the item with the slug and the highest item_sort_key.

    """
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm
    # success_url = (view on this thing we just made/modified)
    success_url = '#'

    # This should (eventually) present a page with four sections:
    # slug, social, presentaiton, content_type, and content.  For now,
    # we'll just present one big page with all the sections joined.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If we find pkid and slug, they must match (avoid fishing and
        # accidents).  Then we are editing that record.  Else we are
        # building a new TBItem.

        # In FormView, we must use the self.kwargs to retrieve the
        # URL parameters. This stems from the View class that
        # transfers the URL parameters to the View instance and
        # assigns kwargs to self.kwargs.
        if 'pkid' in self.kwargs:
            if 'item_slug' in self.kwargs:
                # if both pkid and item_slug are provided, we
                # fetch the corresponding item
                try:
                    tb_item = get_object_or_404(TopicBlogItem,
                                                id=self.kwargs['pkid'],
                                                slug=self.kwargs['item_slug'])
                # We need to handle the case where the inputs are wrong
                # or it would raise a 500 error.
                except ObjectDoesNotExist:
                    raise Http404("L'id ou le slug "
                                  "(la partie lisible de l'URL ex : "
                                  "/tb/s/slug-du-contenu )"
                                  "est / sont incorrect(s)")

            # if we only provide the pkid, we fetch the item with the
            # corresponding pkid. We still check if this item doesn't
            # have an existing slug, as it's a way to avoid fishing.
            else:
                tb_item = get_object_or_404(TopicBlogItem,
                                            id=self.kwargs['pkid'])
                if tb_item.slug != '':
                    raise Http404("Veuillez renseigner le slug du contenu "
                                  "(la partie lisible de l'URL ex : "
                                  "/tb/s/slug-du-contenu )")
        # If we only provide the slug, we load the one with the highest
        # item_sort_key
        else:
            if 'item_slug' in kwargs:
                try:
                    tb_item = TopicBlogItem.objects.filter(
                        slug=self.kwargs['item_slug']
                        ).order_by("item_sort_key").last()
                # If no item with this slug exists, we raise an error.
                except ObjectDoesNotExist:
                    raise Http404("Le slug (la partie lisible de l'URL ex : "
                                  "/tb/s/slug-du-contenu )de cet objet est "
                                  "incorrect")
            else:
                tb_item = None

        context["form"] = TopicBlogItemForm(instance=tb_item)
        return context

    def form_valid(self, form):
        # If this is a new item, it's easy: just save everything in a
        # transaction.
        #
        # If this is not a new item, then we want to see which models
        # have changed.  If something has changed, we want to save it
        # to a new object (not update it in place) and set the TBItem
        # pointer to point to that new object.  As a general rule, we
        # never repersiste objects.  If it's changed, it merits a new
        # object.  Maybe there are some exceptions for very recently
        # created things.
        #
        # We leave the item_sort_key to zero, which means that this
        # item won't immediately be candidate for serving unless it is
        # the only instance of its slug in which case no one knows
        # about it anyway.  This gives us a bit of time to realise
        # we've made an error.
        tb_item = form.save(commit=False)
        tb_item.item_sort_key = randint(0, 65535)
        tb_item.user = User.objects.get(username=self.request.user)
        tb_item.save()

    def post(self, request, *args, **kwargs):
        try:
            instance = TopicBlogItem.objects.get(id=self.kwargs['pkid'])
            form = TopicBlogItemForm(request.POST, request.FILES,
                                     instance=instance)
        except (ObjectDoesNotExist, KeyError):
            form = TopicBlogItemForm(request.POST, request.FILES)

        if form.is_valid():
            # Create a new TBItem and save it.
            # The form_valid function overwrites the FormView one.
            self.form_valid(form)

        return super().form_valid(form)


class TopicBlogItemView(TemplateView):
    """
    This view allows to display Items on their respective templates.

    A user may view the item using its slug when using the
    view_item_by_slug url. In this case, if several items are attached to the
    same slug, the item with the highest item_sort_key is displayed.

    Authorised users may consult specific version of the item using the
    view_item_by_pkid url. The login constraint is not implemented yet.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # There are two ways to access this view : either by
        # providing a pkid AND a item_slug, or by providing a
        # item_slug only.
        # Providing the pkid allows to access a specific version
        # of the item, while the slug alone serves the latest version.
        if 'pkid' in kwargs:
            # if we give both item_slug and pkid, we fetch the item
            if 'item_slug' in kwargs:
                try:
                    tb_item = TopicBlogItem.objects.get(
                        id=kwargs['pkid'],
                        slug=kwargs['item_slug'])
                # We need to handle the case where the inputs are wrong
                # or it would raise a 500 error.
                except ObjectDoesNotExist:
                    raise Http404("L'id ou le slug "
                                  "(la partie lisible de l'URL ex : "
                                  "/tb/admin/view/id/slug-du-contenu )"
                                  " est / sont incorrect(s)")
            # if we only give the pkid
            else:
                try:
                    tb_item = TopicBlogItem.objects.get(id=kwargs['pkid'])
                except ObjectDoesNotExist:
                    raise Http404("Aucun item ne correspond à cet ID")
                if tb_item.slug != "":
                    raise Http404("Le slug (la partie lisible de l'URL ex : "
                                  "/admin/view/slug-du-contenu ) de cet objet"
                                  " est requis")
        # if we only give the item_slug
        else:
            try:
                tb_item = TopicBlogItem.objects.filter(
                    slug=kwargs['item_slug']
                    ).order_by("item_sort_key").last()
            # If no item with this slug exists, we raise an error.
            except ObjectDoesNotExist:
                raise Http404("Le slug (la partie lisible de l'URL ex : "
                              "/tb/s/slug-du-contenu ) de cet objet est "
                              "incorrect")
            # The filter is empty if no item with this slug exists.
            if tb_item is None:
                raise Http404("Aucun item ne correspond à cet ID")

        # The template is set in the model, it's a str referring to
        # an existing template in the app.
        self.template_name = tb_item.template.template_name
        context['page'] = tb_item
        # set_context adds the socials into the context
        tb_item: TopicBlogItem  # Type hint for linter
        context = tb_item.set_context(context)
        return context
