import logging
from datetime import date
import imghdr
from io import BytesIO
from hashlib import sha3_256
from typing import Union
from urllib.parse import urlparse

import requests
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import files
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from lxml import html

from .form import PressMentionForm, PressMentionSearch
from .models import PressMention

logger = logging.getLogger("django")


class PressMentionListView(ListView):
    """Public list view of press citations."""

    model = PressMention
    template_name = "press/press_list_view.html"
    queryset = PressMention.objects.all()
    context_object_name = 'press_mention_list'
    paginate_by = 10


class PressMentionListViewAdmin(PermissionRequiredMixin, ListView):
    """Admin list view of press citations."""

    model = PressMention
    template_name = "press/press_list.html"
    queryset = PressMention.objects.all()
    context_object_name = 'press_mention_list'
    paginate_by = 20
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = PressMentionSearch()
        context["number_pagination_list"] = \
            context["paginator"].get_elided_page_range(
            number=context["page_obj"].number,
            on_each_side=4, on_ends=0)
        if self.request.GET.get("newspaper_name"):
            context["is_not_full"] = True
            context["search_form"].fields["newspaper_name_search"].initial = \
                self.request.GET.get("newspaper_name")
        if self.request.GET.get("search"):
            context["is_not_full"] = True
            context["search_form"].fields["newspaper_name_search"].initial = \
                self.request.GET.get("newspaper_name_search")
            context["search_form"].fields["article_link"].initial = \
                self.request.GET.get("article_link")
            context["search_form"].fields["article_title"].initial = \
                self.request.GET.get("article_title")
            context["search_form"].fields["article_summary"].initial = \
                self.request.GET.get("article_summary")
            context["search_form"].fields["article_date_start"].initial = \
                self.request.GET.get("article_date_start")
            context["search_form"].fields["article_date_end"].initial = \
                self.request.GET.get("article_date_end")
        if self.request.GET.get("press_mention_refresh"):
            update_opengraph_data(
                presmention_id=self.request.GET.get(
                    "press_mention_refresh"))
        return context

    def get_queryset(self):
        if self.request.GET.get("newspaper_name"):
            name = self.request.GET.get("newspaper_name")
            if name:
                return PressMention.objects.filter(newspaper_name=name)
        if self.request.GET.get("search"):
            news_paper = self.request.GET.get("newspaper_name_search")
            link = self.request.GET.get("article_link")
            title = self.request.GET.get("article_title")
            summary = self.request.GET.get("article_summary")
            start_date = self.request.GET.get("article_date_start")
            end_date = self.request.GET.get("article_date_end")
            if start_date > end_date and end_date:
                temp_var = start_date
                start_date = end_date
                end_date = temp_var
            elif start_date and not end_date:
                end_date = date.today()
            elif end_date and not start_date:
                start_date = end_date
            else:
                start_date = date(2000, 1, 1)
                end_date = date.today()

            return PressMention.objects.filter(
                newspaper_name__contains=news_paper,
                article_link__contains=link,
                article_title__contains=title,
                article_summary__contains=summary,
                article_publication_date__range=(start_date, end_date))
        return super().get_queryset()


@csrf_protect
def fetch_opengraph_data(request, url=None, is_view=False) \
        -> Union[tuple, JsonResponse]:
    """Fetch OpenGraph data from a URL.

    Keywords arguments:
    request -- The request object
    url     -- URL to fetch when called from view, request object if called
               via ajax.
    is_view -- if the function is called from a view

    Returns one of the following :
    - a tuple containing the title, description, image, newspaper_name and
    publication_date if the function is called from a view
    - a JSONResponse containing the title, description, image, newspaper_name
    and publication_date if the function is called from browser (Ajax)
    """
    if not is_view:
        url = request.POST["url"]

    try:
        # Some websites may filter the default user agent python-requests
        # We use a custom one to avoid this
        headers = {
            # My Chrome user agent
            "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64)"
                           " AppleWebKit/537.36"
                           " (KHTML, like Gecko) Chrome/108.0.0.0 "
                           "Safari/537.36"),
        }
        # The url comes from the user, but this form is only accessible to
        # authorized users. We trust it as much as we trust the user.
        response = requests.get(url, headers=headers)
        tree = html.fromstring(response.content.decode("utf-8"))
        title = tree.xpath('//meta[@property="og:title"]/@content')
        description = tree.xpath(
            '//meta[@property="og:description"]/@content')
        image = tree.xpath('//meta[@property="og:image"]/@content')
        newspaper_name = tree.xpath(
            '//meta[@property="og:site_name"]/@content')
        publication_date = tree.xpath(
            '//meta[@property="og:article:published_time"]/@content')

        if is_view:
            return title, description, image, newspaper_name, publication_date
        else:
            return JsonResponse({
                "title": title[0] if title else "",
                "description": description[0] if description else "",
                "image": image[0] if image else "",
                "newspaper_name": newspaper_name[0] if newspaper_name else "",
                "publication_date": publication_date[0] if publication_date
                else ""
            }, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"Error during OG data fetch : {e}")
        return None, None, None, None, None


class PressMentionCreateView(PermissionRequiredMixin, CreateView):
    """Admin citation creation view."""

    template_name = "press/press_create.html"
    form_class = PressMentionForm
    permission_required = 'press.press-editor'

    def form_valid(self, form):
        update_opengraph_data(form)
        return super().form_valid(form)


class PressMentionUpdateView(PermissionRequiredMixin, UpdateView):
    """Admin citation update view."""

    model = PressMention
    template_name = "press/press_update.html"
    form_class = PressMentionForm
    success_url = reverse_lazy('press:list_items')
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["newspaper_name_list"] = PressMention.objects.distinct(
        ).order_by('newspaper_name').values_list(
            'newspaper_name', flat=True)
        return context

    def form_valid(self, form):
        update_opengraph_data(form)
        return super().form_valid(form)


class PressMentionDeleteView(PermissionRequiredMixin, DeleteView):
    """Admin citation deletion view."""

    model = PressMention
    template_name = "press/press_delete.html"
    success_url = reverse_lazy('press:list_items')
    permission_required = 'press.press-editor'


class PressMentionDetailView(PermissionRequiredMixin, DetailView):
    """Admin detail view."""

    model = PressMention
    template_name = "press/press_detail.html"
    permission_required = 'press.press-editor'


def update_opengraph_data(form=None, pressmention_id=None):
    """
    Fetch open graph data of a web page.

    This function allow fetch open graph data of an url from
    a form or from the get data of the url and return None.
    """
    if form:
        url = form.cleaned_data['article_link']
        # Settings the default data
        form.instance.og_title = form.cleaned_data['article_title']
        form.instance.og_description = form.cleaned_data['article_summary']
    else:
        press_mention = PressMention.objects.get(
            pk=pressmention_id)
        url = press_mention.article_link
    try:
        page_html = requests.get(url)
    except Exception as e:
        # It would be better to log the status code rather than a
        # semi-meaningless "can't access".
        logger.warning(f"Can't acess {e}.")
        return None
    doc_tree = html.fromstring(page_html.content.decode("utf-8"))
    og_title = doc_tree.xpath('//meta[@property="og:title"]/@content')
    og_description = doc_tree.xpath(
        '//meta[@property="og:description"]/@content')
    og_image_url = doc_tree.xpath('//meta[@property="og:image"]/@content')
    if not og_title or not og_description:
        logger.info(f"No opengraph data at {url}.")
        return None
    else:
        if form:
            form.instance.og_title = og_title[0]
            form.instance.og_description = og_description[0]
        else:
            press_mention.og_title = og_title[0]
            press_mention.og_description = og_description[0]
    try:
        http_response = requests.get(og_image_url[0])
    except IndexError:
        logger.warning("This website doesn't have open graph image.")
        return None
    except requests.exceptions.MissingSchema:
        # If the website doesn't give the full path of the url, try to
        # provide a schema to make a fully qualified URL.
        parsed_uri = urlparse(url)
        protocol_and_domain = f'{parsed_uri.scheme}://{parsed_uri.netloc}/'
        try:
            http_response = requests.get(protocol_and_domain + og_image_url[0])
        except Exception as e:
            logger.warning(f"Can't acess to the open graph image {e}.")
            return None
    if http_response.status_code != requests.codes.ok:
        logger.warning("The link of the open graph "
                       "image may be dead, or doesn't exist.")
        return None

    def get_image_extension(file_contents):
        """Return as a string the image file type.

        Precede with a dot so we can use the output of this function
        direction in appending to the desired filename.

        """
        for tf in imghdr.tests:
            result = tf(file_contents, None)
            if result:
                return "." + result
        logger.warning("Failed to determine image type, {bytes} bytes.".format(
            bytes=len(file_contents)))
        return ""

    # Init the buffered I/O
    image_fp = BytesIO()
    # Write the open graph image contents to its destination.
    image_fp.write(http_response.content)
    # Retrieve the file name of the opengraph image
    raw_image_filename = og_image_url[0]
    base_image_filename = sha3_256(raw_image_filename.encode()
                               ).hexdigest()
    image_filename = base_image_filename + get_image_extension(
        http_response.content)
    if form:
        # Add the image to the PressMention form
        form.instance.og_image.save(image_filename, files.File(image_fp))
        return None
    else:
        # Add the open graph image on the PressMention object
        press_mention.og_image_url.save(image_filename, files.File(image_fp))
        press_mention.save()
        return None


@csrf_protect
@permission_required('press.press-editor')
def check_for_duplicate(request, *args, **kwargs):
    """Check if the provided URL already exists in PressMention."""
    url = request.GET.get("url")
    if url:
        try:
            # Article_link has a unique constraint
            press_mention = PressMention.objects.get(article_link=url)
        except PressMention.DoesNotExist:
            press_mention = None

        if press_mention:
            return JsonResponse(
                {
                    "is_duplicate": True,
                    "edit_url": reverse(
                        'press:update_item',
                        kwargs={
                            'pk': press_mention.pk
                        }
                    )
                }
            )
    return JsonResponse({"is_duplicate": False})
