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
from .models import TopicBlogItem, TopicBlogTemplate, TopicBlogEmail
from .forms import TopicBlogItemForm

logger = logging.getLogger("django")


class TopicBlogBaseEdit(StaffRequiredMixin, FormView):
    """
    Create or modify a concrete TBObject.  This class handles the
    elements common to all TBObject types.

    Fetch a TopicBlogObject and render it for editing.  For additional
    security (avoid phishing), require the pk_id and slug.  If the
    slug is absent, assume it is empty.  If the pk_id is also absent,
    we are creating a new item.

    The derived view must provide model, template_name, and form_class.

    """
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        # In FormView, we must use the self.kwargs to retrieve the URL
        # parameters. This stems from the View class that transfers
        # the URL parameters to the View instance and assigns kwargs
        # to self.kwargs.
        pk_id = self.kwargs.get('pkid', -1)
        slug = self.kwargs.get('the_slug', '')

        if pk_id > 0:
            tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)
            kwargs["form"] = self.form_class(instance=tb_object)
            context = super().get_context_data(**kwargs)
        else:
            tb_object = self.model()
            context = super().get_context_data(**kwargs)
        context['tb_object'] = tb_object
        return context

    def form_valid(self, form):
        tb_object = form.save(commit=False)
        tb_object.user = User.objects.get(username=self.request.user)
        if hasattr(self, "form_post_process"):
            self.form_post_process(tb_object, form)

        # Every modification creates a new item.
        tb_object.pk = None
        tb_object.publication_date = None
        tb_object.save()
        return HttpResponseRedirect(tb_object.get_absolute_url())


class TopicBlogBaseView(TemplateView):
    """
    Render a TopicBlogItem.

    View a TopicBlogObject by published slug.  No authentication
    required.

    The derived view must provide model.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            tb_object = self.model.objects.filter(
                slug=kwargs['the_slug'],
                publication_date__isnull=False
                ).order_by("-publication_date", "-date_modified").first()
        except ObjectDoesNotExist:
            raise Http404("Page non trouvée")
        if tb_object is None:
            raise Http404("Page non trouvée")

        servable = tb_object.get_servable_status()
        if not servable:
            logger.info("TopicBlogBaseView: %s is not servable", tb_object)
            raise HttpResponseServerError("Le serveur a rencontré un problème")

        # The template is set in the model, it's a str referring to an
        # existing template in the app.
        self.template_name = tb_object.template.template_name
        context['page'] = tb_object
        tb_object: self.model  # Type hint for linter
        context = tb_object.set_social_context(context)

        return context


class TopicBlogBaseViewOne(StaffRequiredMixin, TemplateView):
    """
    Render a specific TopicBlogObject.

    The pk_id specifies which object we want.  A slug is an additional
    security measure to prevent probing by pk_id.  If the slug is not
    provided, it is interpreted to be empty, which only makes sense
    during object creation.

    The derived view must provide model.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk_id = kwargs.get('pkid', -1)
        slug = kwargs.get('the_slug', '')
        tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)

        # We set the template in the model.
        self.template_name = tb_object.template.template_name
        context['page'] = tb_object
        tb_object: self.model  # Type hint for linter
        context = tb_object.set_social_context(context)
        context['topicblog_admin'] = True
        return context

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs) # noqa
        pk_id = kwargs.get('pkid', -1)
        the_slug = kwargs.get('the_slug', '')
        tb_object = get_object_or_404(self.model, id=pk_id, slug=the_slug)
        user = User.objects.filter(username=request.user).first()

        try:
            tb_object: self.model
            if tb_object.publish(user):
                self.model.objects.filter(
                    slug=tb_object.slug).exclude(
                        id=tb_object.id).update(publication_date=None)
                tb_object.save()
                return HttpResponseRedirect(tb_object.get_absolute_url())
        except Exception as e:
            logger.error(e)
            logger.error(f"Failed to publish object {pk_id} with" +
                         "slug \"{the_slug}\"")
            return HttpResponseServerError("Failed to publish item")
        # This shouldn't happen.  It's up to us to make sure we've
        # vetted that the user is authorised to publish and that the
        # necessary fields are completed before enabling the publish
        # button.  Therefore, a 500 is appropriate here.
        return HttpResponseServerError()


class TopicBlogBaseList(StaffRequiredMixin, ListView):
    """
    Render a list of TopicBlogObjects.

    """
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'the_slug' in self.kwargs:
            the_slug = self.kwargs['the_slug']
            context['slug'] = the_slug
            context['is_servable'] = self.model.objects.filter(
                slug=the_slug,
                publication_date__isnull=False
                ).exists()
        return context

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of matches for a given the_slug.
        """
        qs = super(ListView, self).get_queryset(*args, **kwargs)
        if 'the_slug' in self.kwargs:
            # If the_slug exists, we use it to filter the view.
            the_slug = self.kwargs['the_slug']
            qs = qs.filter(slug=the_slug).order_by(
                '-publication_date', '-date_modified')
            return qs
        return qs.values('slug') \
                 .annotate(count=Count('slug'),
                           date_modified=Max('date_modified')) \
                 .order_by('-date_modified')


######################################################################
# TopicBlogItem


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


class TopicBlogItemEdit(TopicBlogBaseEdit):
    """
    Create or modify a TBItem.

    """
    model = TopicBlogItem
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb_item = context['tb_object']

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

    def form_post_process(self, tb_item, form):

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


class TopicBlogItemView(TopicBlogBaseView):
    """
    Render a TopicBlogItem.

    """
    model = TopicBlogItem


class TopicBlogItemViewOne(TopicBlogBaseViewOne):
    model = TopicBlogItem


class TopicBlogItemList(TopicBlogBaseList):
    model = TopicBlogItem

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicblogitem_list_one.html'] + names
        else:
            return names

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'the_slug' in self.kwargs:
            context["currently_published"] = context["object_list"].first()

        return context


######################################################################
# TopicBlogEmail

class TopicBlogEmailEdit(TopicBlogBaseEdit):
    model = TopicBlogEmail
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm


class TopicBlogEmailView(TopicBlogBaseView):
    model = TopicBlogEmail


class TopicBlogEmailViewOne(TopicBlogBaseViewOne):
    model = TopicBlogEmail


class TopicBlogEmailList(TopicBlogBaseList):
    model = TopicBlogEmail
