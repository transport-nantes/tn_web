from datetime import datetime, timezone
import logging
from typing import Union

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from mobilito.forms import AddressForm
from mobilito.models import Session

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


class RecordingView(TemplateView):
    template_name = 'mobilito/recording.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        address = self.request.session.get('address')
        city = self.request.session.get('city')
        postcode = self.request.session.get('postcode')
        session_object = Session.objects.create(
            user=self.request.user,
            city=city,
            address=address,
            postcode=postcode,
            start_timestamp=datetime.now(timezone.utc),
        )
        self.request.session["mobilito_session_id"] = session_object.id
        logger.info(
            f'{self.request.user.email} started a new session. '
            f'ID : {session_object.id}')
        return context

    def post(self, request: HttpRequest, *args, **kwargs) \
            -> HttpResponseRedirect:
        now = datetime.now(timezone.utc)
        # Update of associated session
        try:
            session_object: Session = Session.objects.get(
                id=request.session.get('mobilito_session_id'))
            session_object.end_timestamp = now
            session_object.save()
        except Session.DoesNotExist as e:
            logger.error(
                f'{request.user.email} tried to update a non-existing '
                f'session : {e}')

        # Thank you page
        # request.session is used to fill the thank you page
        number_of_pedestrians = request.POST.get('pedestrian')
        number_of_bicycles = request.POST.get('bicycle')
        number_of_cars = request.POST.get('motor-vehicle')
        number_of_public_transports = request.POST.get('public-transport')
        request.session['start_timestamp'] = \
            session_object.start_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        request.session["end_timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
        request.session['number_of_pedestrians'] = number_of_pedestrians
        request.session['number_of_bicycles'] = number_of_bicycles
        request.session['number_of_cars'] = number_of_cars
        request.session['number_of_public_transports'] = \
            number_of_public_transports

        return HttpResponseRedirect(reverse('mobilito:thanks'))

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # If someone accesses the recording page directly,
        # we redirect him to the address form
        if request.session.get('address') is None:
            return HttpResponseRedirect(reverse('mobilito:address_form'))
        return super().get(request, *args, **kwargs)


class ThankYouView(TemplateView):
    template_name = 'mobilito/thanks.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request.session.pop("address", None)
        return super().get(request, *args, **kwargs)


def get_session_object(request: HttpRequest) -> Union[Session, None]:
    try:
        session_object = Session.objects.get(
            id=request.session.get('mobilito_session_id'))
    except Session.DoesNotExist as e:
        logger.error(
            f'{request.user.email} tried to get a non-existing '
            f'session : {e}')
        session_object = None
    return session_object


def create_event(request: HttpRequest) -> HttpResponse:
    """Create a Mobilito event from a POST request"""
    if request.method == 'POST':
        session_object = get_session_object(request)
        event_type = request.POST.get('event_type').upper()
        if session_object:
            session_object.create_event(event_type)
            return HttpResponse(status=200)

        logger.error(f"{request.user.email} tried to create an event from a "
                     "non-existing session")

        return HttpResponse(status=200)

    if request.method == 'GET':
        return HttpResponse(status=403)
