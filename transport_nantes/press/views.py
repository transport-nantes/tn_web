from django.views.generic import ListView, FormView
from .models import PressMention
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from .form import PressMentionForm


class PressMentionListView(ListView):
    model = PressMention
    template_name = "press/press_list_view.html"
    queryset = PressMention.objects.all().order_by(
        '-article_publication_date')[:4]
    context_object_name = 'press_mention_list'


class PressMentionListViewAdmin(PermissionRequiredMixin, ListView):
    model = PressMention
    template_name = "press/press_list.html"
    queryset = PressMention.objects.all().order_by('-article_publication_date')
    context_object_name = 'press_mention_list'
    permission_required = 'press.press-editor'


class PressMentionCreateView(PermissionRequiredMixin, FormView):
    template_name = "press/press_create.html"
    form_class = PressMentionForm
    success_url = reverse_lazy('press:new_item')
    permission_required = 'press.press-editor'

    def form_valid(self, form):
        name = form.cleaned_data['newspaper_name']
        link = form.cleaned_data['article_link']
        title = form.cleaned_data['article_title']
        summary = form.cleaned_data['article_summary']
        publication_date = form.cleaned_data['article_publication_date']
        press_mention = PressMention.objects.create(
            newspaper_name=name,
            article_link=link,
            article_title=title,
            article_summary=summary,
            article_publication_date=publication_date,
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["press_mention_list"] = PressMention.objects.all().order_by(
            "-article_publication_date")
        return context
