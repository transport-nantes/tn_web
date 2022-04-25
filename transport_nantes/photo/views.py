"""Application to manage a photo competition."""

from django.views.generic import (TemplateView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin


class UploadEntry(LoginRequiredMixin, CreateView):
    """
    Hello.

    x.
    """

    pass


class Confirmation(TemplateView):
    """
    Hello.

    x.
    """

    pass
