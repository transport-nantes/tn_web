from attr import fields
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
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
    queryset = PressMention.objects.all()
    ordering = ['-article_publication_date']
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
    success_url = reverse_lazy('press:new_item')
    permission_required = 'press.press-editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["press_mention_list"] = PressMention.objects.all().order_by(
            "-article_publication_date")
        return context

class PressMentionUpdateView(PermissionRequiredMixin,UpdateView):
    model = PressMention
    template_name = "press/press_update.html"
    form_class = PressMentionForm
    success_url = reverse_lazy('press:list_items')
    permission_required = 'press.press-editor'

class PressMentionDeleteView(PermissionRequiredMixin,DeleteView):
    model = PressMention
    template_name = "press/press_delete.html"
    permission_required = 'press.press-editor'
    success_url = reverse_lazy('press:list_items')
