import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from mobilito.forms import AddressForm

logger = logging.getLogger("django")


class MobilitoView(TemplateView):
    template_name = 'mobilito/index.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('mobilito:tutorial'))
        return super().get(request, *args, **kwargs)


class TutorialView(TemplateView):
    template_name = 'mobilito/tutorial.html'


class AddressFormView(LoginRequiredMixin, FormView):
    template_name = 'mobilito/address_form.html'
    form_class = AddressForm
    success_url = reverse_lazy('mobilito:recording')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Clear session data if user had filled the form before.
        self.request.session['address'] = None
        self.request.session['city'] = None
        self.request.session['postcode'] = None
        return context

    def form_valid(self, form):
        address, city, postcode = (
            form.cleaned_data['address'],
            form.cleaned_data['city'],
            form.cleaned_data['postcode'],
        )
        self.request.session['address'] = address
        self.request.session['city'] = city
        self.request.session['postcode'] = postcode
        logger.info(
            f'{self.request.user.email} filled address form.\n'
            f'Address saved: {address}, {city}, {postcode}')
        return super().form_valid(form)
