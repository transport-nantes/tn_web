from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from .models import PressMention
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .form import PressMentionForm, PressMentionSearch
import requests
from lxml import html
from django.core import files
from io import BytesIO
import requests
import logging
from datetime import date
logger = logging.getLogger("django")


class PressMentionListView(ListView):
    model = PressMention
    template_name = "press/press_list_view.html"
    queryset = PressMention.objects.all()[:30]
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
        try:
            # Check if the website is accessible
            page = requests.get(form.cleaned_data['article_link'])
        except Exception as e:
                logger.error(f"Exeption when saving Pressmention {e}.")
                form._errors['article_link'] = \
                    ['Le liens est incorrect ou le site web est indisponible.']
                return super().form_invalid(form)
        tree = html.fromstring(page.content.decode("utf-8"))
        og_title = tree.xpath('//meta[@property="og:title"]/@content')
        og_description = tree.xpath(
            '//meta[@property="og:description"]/@content')
        og_image = tree.xpath('//meta[@property="og:image"]/@content')
        form.instance.og_title = og_title[0]
        form.instance.og_description = og_description[0]
        resp = requests.get(og_image[0])
        if resp.status_code != requests.codes.ok:
            logger.error("The link of the open graph image may be dead, or doesn't exist.")
            form._errors['article_link'] = \
                ['Le site ne contient pas de meta données Open Graph valide.']
            return super().form_invalid(form)
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
