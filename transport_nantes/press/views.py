import logging
from datetime import date
from io import BytesIO
from typing import Union
from urllib.parse import urlparse

import requests
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core import files
from django.http import HttpResponseRedirect, JsonResponse
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, FormView)
from lxml import html

from .form import PressMentionForm, PressMentionSearch, PressMentionUrlForm
from .models import PressMention

logger = logging.getLogger("django")


class PressMentionListView(ListView):
    model = PressMention
    template_name = "press/press_list_view.html"
    queryset = PressMention.objects.all()
    context_object_name = 'press_mention_list'
    paginate_by = 10


class PressMentionListViewAdmin(PermissionRequiredMixin, ListView):
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


class PressMentionPreCreateView(PermissionRequiredMixin, FormView):
    form_class = PressMentionUrlForm
    template_name = "press/press_pre_create.html"
    permission_required = 'press.press-editor'

    def form_valid(self, form):
        url = form.cleaned_data["article"]
        title, description, image, newspaper_name, publication_date = \
            fetch_opengraph_data(self.request, url, isView=True)
        return HttpResponseRedirect(
            reverse_lazy("press:new_item") +
            "?title={}&description={}&image={}&newspaper_name={}"
            "&publication_date={}&url={}".format(
                    title[0] if title else "",
                    description[0] if description else "",
                    image[0] if image else "",
                    newspaper_name[0] if newspaper_name else "",
                    publication_date[0][:10] if publication_date else "",
                    url
            )
        )


@csrf_protect
def fetch_opengraph_data(request, url=None, isView=False) \
        -> Union[tuple, JsonResponse]:
    """Fetch OpenGraph data from a URL.

    Keywords arguments:
    url -- the URL to fetch when called from view, request object if called ajax
    isView -- if the function is called from a view

    Returns one of the following :
    - a tuple containing the title, description, image, newspaper_name and
    publication_date if the function is called from a view
    - a JSONResponse containing the title, description, image, newspaper_name
    and publication_date if the function is called from browser (Ajax)
    """
    if not isView:
        url = request.POST["url"]

    try:
        response = requests.get(url)
        tree = html.fromstring(response.content)
        title = tree.xpath('//meta[@property="og:title"]/@content')
        description = tree.xpath(
            '//meta[@property="og:description"]/@content')
        image = tree.xpath('//meta[@property="og:image"]/@content')
        newspaper_name = tree.xpath('//meta[@property="og:site_name"]/@content')
        publication_date = tree.xpath(
            '//meta[@property="og:article:published_time"]/@content')

        if isView:
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
    template_name = "press/press_create.html"
    form_class = PressMentionForm
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context["form"]
        if self.request.GET.get("url"):
            form.fields["article_link"].initial = self.request.GET.get("url")
        if self.request.GET.get("title"):
            form.fields["article_title"].initial = self.request.GET.get("title")
        if self.request.GET.get("description"):
            form.fields["article_summary"].initial = \
                self.request.GET.get("description")
        if self.request.GET.get("newspaper_name"):
            form.fields["newspaper_name"].initial = \
                self.request.GET.get("newspaper_name")
        if self.request.GET.get("publication_date"):
            date = self.request.GET.get("publication_date")[:10]
            form.fields["article_publication_date"].initial = date
        return context

    def form_valid(self, form):
        update_opengraph_data(form)
        return super().form_valid(form)


class PressMentionUpdateView(PermissionRequiredMixin, UpdateView):
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
    model = PressMention
    template_name = "press/press_delete.html"
    success_url = reverse_lazy('press:list_items')
    permission_required = 'press.press-editor'


class PressMentionDetailView(PermissionRequiredMixin, DetailView):
    model = PressMention
    template_name = "press/press_detail.html"
    permission_required = 'press.press-editor'


def update_opengraph_data(form=False, presmention_id=None):
    """
    This function allow fetch open graph data of an url from
    a form or from the get data of the url and return None
    """
    if form:
        url = form.cleaned_data['article_link']
        # Settings the default data
        form.instance.og_title = form.cleaned_data['article_title']
        form.instance.og_description = form.cleaned_data['article_summary']
        form.instance.newspaper_name = form.cleaned_data['newspaper_name']
    else:
        press_mention = PressMention.objects.get(
            pk=presmention_id)
        url = press_mention.article_link
    try:
        page = requests.get(url)
    except Exception as e:
        # It would be better to log the status code rather than a
        # semi-meaningless "can't access".
        logger.warning(f"Can't acess {e}.")
        return None
    tree = html.fromstring(page.content.decode("utf-8"))
    og_title = tree.xpath('//meta[@property="og:title"]/@content')
    og_description = tree.xpath(
        '//meta[@property="og:description"]/@content')
    og_image = tree.xpath('//meta[@property="og:image"]/@content')
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
        resp = requests.get(og_image[0])
    except IndexError:
        logger.warning("This website doesn't have open graph image.")
        return None
    except requests.exceptions.MissingSchema:
        # if the website doest give the full path of the url
        parsed_uri = urlparse(url)
        protocol_and_domain = f'{parsed_uri.scheme}://{parsed_uri.netloc}/'
        try:
            resp = requests.get(protocol_and_domain + og_image[0])
        except Exception as e:
            logger.warning(f"Can't acess to the open graph image {e}.")
            return None
    if resp.status_code != requests.codes.ok:
        logger.warning("The link of the open graph "
                       "image may be dead, or doesn't exist.")
        return None
    else:
        # Init the buffered I/O
        fp = BytesIO()
        # Copy the open graph image
        fp.write(resp.content)
        # Retrieve the file name of the opengraph image
        file_name = og_image[0].split('/')[-1]
        if form:
            # Add the image to the PressMention form
            form.instance.og_image.save(file_name, files.File(fp))
            return None
        else:
            # Add the open graph image on the PressMention object
            press_mention.og_image.save(file_name, files.File(fp))
            press_mention.save()
            return None
