from asso_tn.utils import StaffRequiredMixin
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from topicblog.models import EmailCampaign

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


class EmailCampaignsDashboardView(PermissionRequiredMixin,
                                  LoginRequiredMixin,
                                  ListView):
    """Dashboard of email campaigns"""
    # Login & Permission
    login_url = reverse_lazy("authentication:login")
    permission_required = ('topicblog.tbe.may_send', 'topicblog.tbp.may_send')
    # ListView
    model = EmailCampaign
    template_name = 'dashboard/email_campaigns.html'
    ordering = ('-timestamp')


class EmailCampaignDetailView(PermissionRequiredMixin,
                              LoginRequiredMixin,
                              DetailView):
    """Detail of an email campaign"""
    # Login & Permission
    login_url = reverse_lazy("authentication:login")
    permission_required = ('topicblog.tbe.may_send', 'topicblog.tbp.may_send')
    # DetailView
    template_name = 'dashboard/email_campaign_details.html'
    model = EmailCampaign
    context_object_name = 'campaign'
