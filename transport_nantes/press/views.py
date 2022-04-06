from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from .models import PressMention
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .form import PressMentionForm
import requests
from lxml import html
from django.core import files
from io import BytesIO
import requests
import logging

logger = logging.getLogger("django")


class PressMentionListView(ListView):
    model = PressMention
    template_name = "press/press_list_view.html"
    queryset = PressMention.objects.all()[:4]
    context_object_name = 'press_mention_list'


class PressMentionListViewAdmin(PermissionRequiredMixin, ListView):
    model = PressMention
    template_name = "press/press_list.html"
    queryset = PressMention.objects.all()
    context_object_name = 'press_mention_list'
    paginate_by = 20
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["number_pagination_list"] = \
            context["paginator"].get_elided_page_range(
            number=context["page_obj"].number,
            on_each_side=4, on_ends=0)
        if self.request.GET.get("newspaper_name"):
            context["is_not_full"] = True
        return context

    def get_queryset(self):
        if self.request.GET.get("newspaper_name"):
            name = self.request.GET.get("newspaper_name")
            if name:
                return PressMention.objects.filter(newspaper_name=name)
        return super().get_queryset()


class PressMentionCreateView(PermissionRequiredMixin, CreateView):
    template_name = "press/press_create.html"
    form_class = PressMentionForm
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["press_mention_list"] = PressMention.objects.all().order_by(
            "-article_publication_date")[:5]
        context["newspaper_name_list"] = PressMention.objects.distinct(
        ).order_by('newspaper_name').values_list(
            'newspaper_name', flat=True)
        return context

    def form_valid(self, form):
        page = requests.get(form.cleaned_data['article_link'])
        tree = html.fromstring(page.content.decode("utf-8"))
        og_title = tree.xpath('//meta[@property="og:title"]/@content')
        og_description = tree.xpath(
            '//meta[@property="og:description"]/@content')
        og_image = tree.xpath('//meta[@property="og:image"]/@content')
        form.instance.og_title = og_title[0]
        form.instance.og_description = og_description[0]
        resp = requests.get(og_image[0])
        if resp.status_code != requests.codes.ok:
            logger.error(f"The url of the open graph image is not good.")
        else:
            fp = BytesIO()
            fp.write(resp.content)
            file_name = og_image[0].split('/')[-1]
            form.instance.og_image.save(file_name, files.File(fp))
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


class PressMentionDeleteView(PermissionRequiredMixin, DeleteView):
    model = PressMention
    template_name = "press/press_delete.html"
    success_url = reverse_lazy('press:list_items')
    permission_required = 'press.press-editor'


class PressMentionDetailView(PermissionRequiredMixin, DetailView):
    model = PressMention
    template_name = "press/press_detail.html"
    permission_required = 'press.press-editor'
