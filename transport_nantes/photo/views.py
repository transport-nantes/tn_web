"""Application to manage a photo competition."""

from django.urls import reverse_lazy
from django.views.generic import (TemplateView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PhotoEntry


class UploadEntry(LoginRequiredMixin, CreateView):
    """
    Form to collect Photo entries
    """

    pass


class Confirmation(TemplateView):
    """
    Confirmation page after successful submit of a PhotoEntry
    """

    pass
