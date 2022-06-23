"""Application to manage a photo competition."""
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from asso_tn.utils import make_timed_token, token_valid
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

    def get(self, request, *args, **kwargs):
        logger.info(f"UploadEntry.get() from {request.user}")
        return super().get(request, *args, **kwargs)

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

    def form_valid(self, form):
        """
        Override the form_valid method to add the user's submission to session
        """
        self.object = form.save()
        encoded_object_id = make_timed_token(
            string_key="", int_key=self.object.id, minutes=60*24*30)
        self.success_url += f"?submission={encoded_object_id}"
        return HttpResponseRedirect(self.get_success_url())


class Confirmation(TemplateView):
    """
    Confirmation page after successful submit of a PhotoEntry
    """
    template_name = 'photo/confirmation.html'

    def get(self, request, *args, **kwargs):
        logger.info(f"Confirmation.get() from {request.user}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_submitted_photo = None
        submission_token = self.request.GET.get("submission")
        string_key, photo_id = token_valid(submission_token)

        if photo_id and string_key == "":
            last_submitted_photo = \
                PhotoEntry.objects.get(id=photo_id)
        if last_submitted_photo:
            context["submitted_photo"] = \
                last_submitted_photo.submitted_photo.url

        return context
