from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from asso_tn.utils import StaffRequiredMixin
from django.urls import reverse_lazy

from .forms import SignatureForm


class DashboardIndex(StaffRequiredMixin, TemplateView):
    """Present dashboard index.

    I haven't finished designing this, so it's anybody's guess what I
    mean here.  I need to see something rough to figure out what I
    want.

    """
    template_name = 'dashboard/index.html'
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SignatureView(LoginRequiredMixin, FormView):
    """Form to generate a mail signature"""
    template_name = 'dashboard/signature.html'
    form_class = SignatureForm
