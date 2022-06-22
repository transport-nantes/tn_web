"""Application to manage a photo competition."""
import logging
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .forms import PhotoEntryForm
from .models import PhotoEntry
from mailing_list.models import MailingList
from mailing_list.events import subscribe_user_to_list

logger = logging.getLogger("django")


class UploadEntry(LoginRequiredMixin, CreateView):
    """
    Form to collect Photo entries
    """
    model = PhotoEntry
    form_class = PhotoEntryForm

    success_url = reverse_lazy('photo:confirmation')

    def post(self, request, *args, **kwargs):
        """
        Override the post method to add the user to the form
        """
        form = self.get_form()
        self.object = None
        form.instance.user = request.user
        if form.is_valid():
            try:
                logger.info("Received photo submission.")
                mailing_list = MailingList.objects.get(
                    mailing_list_token="operation-pieton")
                user = request.user
                subscribe_user_to_list(user, mailing_list)
                logger.info(f"Subscribed user {user} to list {mailing_list}.")
            except ObjectDoesNotExist:
                logger.error("Mailing list operation-pieton does not exist")

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Confirmation(TemplateView):
    """
    Confirmation page after successful submit of a PhotoEntry
    """
    template_name = 'photo/confirmation.html'
