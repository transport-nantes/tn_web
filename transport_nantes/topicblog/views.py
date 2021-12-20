from collections import Counter
import logging

from django.db.models import Count, Max
from django.http import Http404, HttpResponseServerError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy

from asso_tn.utils import StaffRequiredMixin, StaffRequired
from asso_tn.utils import SuperUserRequiredMixin
from .models import TopicBlogItem, TopicBlogTemplate
from .forms import TopicBlogItemForm

logger = logging.getLogger("django")


class TopicBlogItemEdit(StaffRequiredMixin, FormView):
    """Create or modify a TBItem.

    Fetch a TopicBlogItem and render it for editing.  For additional
    security (avoid fishing), require the pk_id and slug.  If the slug
    is absent, assume it is empty.  If the pk_id is also absent, we
    are creating a new item.

    Requires authorisation.

    """
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm
    login_url = reverse_lazy("authentication:login")

    # This should (eventually) present a page with four sections:
    # slug, social, presentation, content_type, and content.  For now,
    # we'll just present one big page with all the sections joined.

    def get_context_data(self, **kwargs):
        # In FormView, we must use the self.kwargs to retrieve the URL
        # parameters. This stems from the View class that transfers
        # the URL parameters to the View instance and assigns kwargs
        # to self.kwargs.
        pk_id = self.kwargs.get('pkid', -1)
        slug = self.kwargs.get('item_slug', '')

        if pk_id > 0:
            try:
                tb_item = get_object_or_404(TopicBlogItem, id=pk_id, slug=slug)
                kwargs["form"] = TopicBlogItemForm(instance=tb_item)
                context = super().get_context_data(**kwargs)
            except ObjectDoesNotExist:
                raise Http404
        else:
            tb_item = TopicBlogItem()
            context = super().get_context_data(**kwargs)

        # Sets if the "Créer un variant" button should be displayed.
        context["variant_available"] = context["form"].variant_available
        # Sets if the "Sauvegarder" button should be displayed.
        context["is_editable"] = context["form"].is_editable

        context["form_admin"] = ["slug", "template", "title", "header_image",
                                 "header_title", "header_description",
                                 "header_slug", "content_type"]
        context["form_content_a"] = ["body_text_1_md", "cta_1_slug",
                                     "cta_1_label", "body_text_2_md",
                                     "cta_2_slug", "cta_2_label", ]
        context["form_content_b"] = ["body_image", "body_image_alt_text",
                                     "body_text_3_md", "cta_3_slug",
                                     "cta_3_label", ]
        context["form_social"] = ["social_description", "twitter_title",
                                  "twitter_description", "twitter_image",
                                  "og_title", "og_description", "og_image", ]

        context["slug_fields"] = tb_item.get_slug_fields()

        return context

    def form_valid(self, form):
        # If this is a new item and it's valid, save it.
        #
        # If this is valid but is not a new item, then save it as a
        # variant.  As a general rule, we never repersist objects.
        # If it's changed, it merits a new object.  Maybe there are
        # some exceptions for very recently created things.
        #
        # We leave the item_sort_key to zero, which means that this
        # item won't immediately be candidate for serving unless it is
        # the only instance of its slug in which case no one knows
        # about it anyway.  This gives us a bit of time to realise
        # we've made an error.
        tb_item = form.save(commit=False)
        tb_item.item_sort_key = 0
        tb_item.user = User.objects.get(username=self.request.user)

        # If we are editing an existing item, the ImageField values
        # won't be copied over -- they aren't included in the rendered
        # form.  Checking the "clear" box in the form will still clear
        # the image fields if needed.
        #
        # This is largely because we're using FormView instead of
        # CreateView / UpdateView.
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            existing_item: TopicBlogItem
            existing_item = TopicBlogItem.objects.get(id=pkid)
            image_fields = existing_item.get_image_fields()
            for field in image_fields:
                if field in form.cleaned_data and \
                        form.cleaned_data[field] is None:
                    setattr(tb_item, field, getattr(existing_item, field))

        # We're in the time period bewteen publication and
        # expiry of editing possibilities
        if tb_item.publication_date and "sauvegarder" in self.request.POST:
            # Make unservable the item before creating a new variant.
            tb_item.servable = False
            tb_item.save()

        # Every modification creates a new item (copy or variant)
        tb_item.pk = None

        # To the difference of copies generated by the edit action,
        # variants do keep the servable status.
        if "create_variant" in self.request.POST:
            tb_item.publication_date = None

        tb_item.save()
        return HttpResponseRedirect(tb_item.get_absolute_url())


@StaffRequired
def get_slug_suggestions(request):
    """Return a JSON list of suggested slugs.

    This is a helper function for the AJAX call to get the list of
    suggested slugs.  It is called from the template.

    """
    partial_slug = request.GET.get('partial_slug')
    slug_list = TopicBlogItem.objects.filter(
        slug__contains=partial_slug).order_by("-id")[:20]
    slug_list = slug_list.values_list('slug', flat=True)
    # Why did we use set instead of applying DISTINCT() ?
    # Because Django doesn't support DISTINCT(*field) on
    # databases other than Postgres. We tried to use raw queries
    # but it proved to be unsuccessful.
    slug_list = set(slug_list)
    return JsonResponse(list(slug_list), safe=False)


@StaffRequired
def update_template_list(request):
    """
    Uses a content type passed through Ajax to render
    a dropdown list of templates associated with this
    content type for the user to choose from.
    """
    content_type = request.GET.get('content_type')
    templates = TopicBlogTemplate.objects.filter(
        content_type=content_type)
    return render(request, 'topicblog/template_dropdown.html',
                  {'templates': templates})


class TopicBlogItemView(TemplateView):
    """Render a TopicBlogItem.

    View a TopicBlogItem by slug.  If multiple items share a slug, we
    choose the one that is currently prioritised (has greatest
    item_sort_key).  No authentication required.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            tb_item = TopicBlogItem.objects.filter(
                slug=kwargs['item_slug'],
                publication_date__isnull=False,
                servable=True
                ).order_by("item_sort_key").last()
        except ObjectDoesNotExist:
            raise Http404("Page non trouvée")
        if tb_item is None:
            raise Http404("Page non trouvée")

        servable = tb_item.get_servable_status()
        if not servable:
            logger.info("TopicBlogItemView: %s is not servable", tb_item)
            raise HttpResponseServerError("Le serveur a rencontré un problème")

        # The template is set in the model, it's a str referring to an
        # existing template in the app.
        self.template_name = tb_item.template.template_name
        context['page'] = tb_item
        tb_item: TopicBlogItem  # Type hint for linter
        context = tb_item.set_social_context(context)
        context["banner_is_present"] = True
        context["banner_text"] = "C’est grâce à votre soutien que nous pouvons agir en toute indépendance."
        context["banner_button_text"] = "Je participe"
        context["banner_button_link"] = reverse('stripe_app:stripe')

        return context


class TopicBlogItemViewOne(StaffRequiredMixin, TemplateView):
    """Render a specific TopicBlogItem.

    Render a specific TopicBlogItem.  That is, we require the pk_id to
    specify which item we want.  A slug is an additional required
    argument as an additional security measure to prevent probing by
    pk_id.  (If the slug is not provided, it is interpreted to be
    empty, which only makes sense during object creation.)

    Requires authorisation.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Default is not a valid pk id, so will 404.
        pk_id = kwargs.get('pkid', -1)
        slug = kwargs.get('item_slug', '')
        try:
            tb_item = TopicBlogItem.objects.get(id=pk_id, slug=slug)
        except ObjectDoesNotExist:
            raise Http404

        # We set the template in the model.
        self.template_name = tb_item.template.template_name
        context['page'] = tb_item
        tb_item: TopicBlogItem  # Type hint for linter
        context = tb_item.set_social_context(context)
        context['topicblog_admin'] = True
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        pk_id = kwargs.get('pkid', -1)
        item_slug = kwargs.get('item_slug', '')
        tb_item = get_object_or_404(TopicBlogItem, id=pk_id, slug=item_slug)

        try:
            tb_item: TopicBlogItem
            if tb_item.publish():
                tb_item.save()
                return HttpResponseRedirect(tb_item.get_absolute_url())
        except Exception as e:
            logger.error(e)
            logger.error(f"Failed to publish article {pk_id} with" +
                         "slug \"{item_slug}\"")
            return HttpResponseServerError("Failed to publish item")
        # This shouldn't happen.  It's up to us to make sure we've
        # vetted that the user is authorised to publish and that the
        # necessary fields are completed before enabling the publish
        # button.  Therefore, a 500 is appropriate here.
        return HttpResponseServerError()


class TopicBlogItemList(StaffRequiredMixin, ListView):
    """Render a list of TopicBlogItems.

    It's then displayed in the topicblogitem_list template.

    """
    model = TopicBlogItem
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'item_slug' in self.kwargs:
            item_slug = self.kwargs['item_slug']
            context['slug'] = item_slug
            context['is_servable'] = TopicBlogItem.objects.filter(
                slug=item_slug,
                publication_date__isnull=False,
                servable=True
                ).exists()
        return context

    def get_template_names(self):
        names = super().get_template_names()
        if 'item_slug' in self.kwargs:
            return ['topicblog/topicblogitem_list_one.html'] + names
        else:
            return names


    def get_queryset(self, *args, **kwargs):
        """Return a queryset of matches for a given item_slug.
        """
        qs = super(ListView, self).get_queryset(*args, **kwargs)
        if 'item_slug' in self.kwargs:
            # If item_slug exists, we use it to filter the view.
            item_slug = self.kwargs['item_slug']
            qs = qs.filter(slug=item_slug).order_by(
                '-date_modified','-publication_date')
            return qs
        # Should sort by date_modified, but that will be ugly until
        # it's been in production for a bit.  So just leave it here
        # that we should drop the sort on publication_date and only
        # use date_modified after a bit.  Jeff, 11 Dec 2021.
        return qs.values('slug') \
                 .annotate(count=Count('slug'),
                           date_modified=Max('date_modified')) \
                 .order_by('-date_modified')

@StaffRequired
def get_slug_dict(request):
    """Return a list of all existing slugs"""
    qs = TopicBlogItem.objects.order_by('slug').values('slug')
    dict_of_slugs = Counter([item['slug'] for item in qs])
    return JsonResponse(dict_of_slugs, safe=False)


@StaffRequired
def get_url_list(request):
    """Return an url directing to a list of items
    given a slug.
    """
    slug = request.GET.get('slug')
    url = reverse("topicblog:list_items_by_slug", args=[slug])
    return JsonResponse({'url': url})
