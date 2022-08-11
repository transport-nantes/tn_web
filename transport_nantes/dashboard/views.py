from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from topicblog.models import EmailCampaign

from .forms import SignatureForm


class DashboardIndex(PermissionRequiredMixin, TemplateView):
    """Present dashboard index.

    I haven't finished designing this, so it's anybody's guess what I
    mean here.  I need to see something rough to figure out what I
    want.

    """
    permission_required = 'dashboard.dashboard.may_see'
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

    def post(self, request, *args, **kwargs):
        """Handle POST requests
        Post requests are made to search user from its mail address,
        and redirect to the user's send records detail page.
        """
        # Get the user from the POST request
        try:
            user = User.objects.get(email=request.POST['email'])
        except User.DoesNotExist:
            user = None

        if user:
            return HttpResponseRedirect(
                reverse_lazy("dashboard:user_send_records",
                             kwargs={'pk': user.pk}))
        else:
            messages.add_message(
                request, messages.ERROR,
                "Aucun utilisateur ne correspond à cette adresse.")
            return self.get(request, *args, **kwargs)


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


class UserSendRecordsDetailView(PermissionRequiredMixin,
                                LoginRequiredMixin,
                                DetailView):
    """Detail of an email campaign"""
    # Login & Permission
    login_url = reverse_lazy("authentication:login")
    permission_required = ('topicblog.tbe.may_send', 'topicblog.tbp.may_send')
    # DetailView
    template_name = 'dashboard/user_send_records_details.html'
    model = User
    context_object_name = 'user_object'
