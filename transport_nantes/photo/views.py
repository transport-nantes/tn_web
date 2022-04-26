"""Application to manage a photo competition."""

from django.urls import reverse_lazy
from django.views.generic import (TemplateView, CreateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PhotoEntry


class UploadEntry(LoginRequiredMixin, CreateView):
    """
    Form to collect Photo entries
    """
    model = PhotoEntry
    fields = ['category', 'submitted_photo', 'relationship_to_competition',
              'photo_location', 'photo_kit', 'technical_notes',
              'photographer_comments']
    success_url = reverse_lazy('photo:confirmation')

    def post(self, request, *args, **kwargs):
        """
        Override the post method to add the user to the form
        """
        form = self.get_form()
        self.object = None
        form.instance.user = request.user
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class Confirmation(TemplateView):
    """
    Confirmation page after successful submit of a PhotoEntry
    """
    template_name = 'photo/confirmation.html'
