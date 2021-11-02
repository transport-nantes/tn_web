from collections import Counter

from django.http import Http404
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse


from asso_tn.utils import StaffRequiredMixin, StaffRequired
from .models import TopicBlogItem, TopicBlogTemplate
from .forms import TopicBlogItemForm


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
    success_url = '#'
    login_url = "/admin/login/"

    # This should (eventually) present a page with four sections:
    # slug, social, presentation, content_type, and content.  For now,
    # we'll just present one big page with all the sections joined.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # In FormView, we must use the self.kwargs to retrieve the URL
        # parameters. This stems from the View class that transfers
        # the URL parameters to the View instance and assigns kwargs
        # to self.kwargs.
        pk_id = self.kwargs.get('pkid', -1)
        slug = self.kwargs.get('item_slug', '')

        if pk_id > 0:
            try:
                tb_item = get_object_or_404(TopicBlogItem, id=pk_id, slug=slug)
            except ObjectDoesNotExist:
                raise Http404("Page non trouvée")
        else:
            tb_item = None

        context["form"] = TopicBlogItemForm(instance=tb_item)
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
        tb_item.save()
        return tb_item

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
            tb_item = self.form_valid(form)
            # Type hint
            tb_item: TopicBlogItem
            context = self.get_context_data()
            context['success'] = True
            context['created_item_view_URL'] = tb_item.get_absolute_url()
            context['created_item_edit_URL'] = tb_item.get_edit_url()

            return render(request, 'topicblog/tb_item_edit.html', context)

        else:
            # The form is invalid.  Re-render the form with error
            # messages.
            context = self.get_context_data()
            context['success'] = False
            context['form'] = form

            return render(request, 'topicblog/tb_item_edit.html', context)


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
                slug=kwargs['item_slug']
                ).order_by("item_sort_key").last()
        except ObjectDoesNotExist:
            raise Http404("Page non trouvée")
        if tb_item is None:
            raise Http404("Page non trouvée")

        # The template is set in the model, it's a str referring to an
        # existing template in the app.
        self.template_name = tb_item.template.template_name
        context['page'] = tb_item
        # set_context adds the socials into the context
        tb_item: TopicBlogItem  # Type hint for linter
        context = tb_item.set_context(context)
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
            raise Http404("Page non trouvée")

        # The template is set in the model, it's a str referring to an
        # existing template in the app.
        self.template_name = tb_item.template.template_name
        context['page'] = tb_item
        # set_context adds the socials into the context
        tb_item: TopicBlogItem  # Type hint for linter
        context = tb_item.set_context(context)
        return context


class TopicBlogItemList(StaffRequiredMixin, ListView):
    """Render a list of TopicBlogItems.

    It's then displayed in the topicblogitem_list template.

    """
    model = TopicBlogItem
    login_url = "/admin/login/"

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of matches for a given item_slug.
        """
        qs = super(ListView, self).get_queryset(*args, **kwargs)
        if 'item_slug' in self.kwargs:
            # If item_slug exists, we use it to filter the view.
            item_slug = self.kwargs['item_slug']
            qs = qs.filter(slug=item_slug)
        return qs


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
