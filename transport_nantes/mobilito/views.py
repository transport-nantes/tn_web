from datetime import datetime, timezone
import logging
from user_agents import parse
from typing import Union

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from mobilito.models import MobilitoUser, Session
from mobilito.forms import AddressForm

logger = logging.getLogger("django")


class MobilitoView(TemplateView):
    """Present Mobilito landing page.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/index.html'


class TutorialView(TemplateView):
    """Present the tutorial.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/tutorial.html'


class AddressFormView(LoginRequiredMixin, FormView):
    """Present the address form.
    The form is optional to fill.
    """

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
        address, city, postcode, country = (
            form.cleaned_data['address'],
            form.cleaned_data['city'],
            form.cleaned_data['postcode'],
            form.cleaned_data['country'],
        )
        self.request.session['address'] = address
        self.request.session['city'] = city
        self.request.session['postcode'] = postcode
        self.request.session['country'] = country
        logger.info(
            f'{self.request.user.email} filled address form.\n'
            f'Address saved: {address}, {city}, {postcode}, {country}')
        return super().form_valid(form)


class RecordingView(TemplateView):
    template_name = 'mobilito/recording.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        address = self.request.session.get('address')
        city = self.request.session.get('city')
        postcode = self.request.session.get('postcode')
        country = self.request.session.get('country')
        user_agent = parse(self.request.META.get('HTTP_USER_AGENT'))
        user = MobilitoUser.objects.get_or_create(
            user=self.request.user)[0]
        session_object = Session.objects.create(
            user=user,
            city=city,
            address=address,
            postcode=postcode,
            country=country,
            user_browser=str(user_agent),
            start_timestamp=datetime.now(timezone.utc),
        )
        self.request.session["mobilito_session_id"] = session_object.id
        logger.info(
            f'{self.request.user.email} started a new session '
            f'id={session_object.id}')
        return context

    def post(self, request: HttpRequest, *args, **kwargs) \
            -> HttpResponseRedirect:
        now = datetime.now(timezone.utc)
        number_of_pedestrians = request.POST.get('pedestrian')
        number_of_bicycles = request.POST.get('bicycle')
        number_of_cars = request.POST.get('motor-vehicle')
        number_of_public_transports = request.POST.get('public-transport')
        # Update of associated session
        try:
            session_object: Session = Session.objects.get(
                id=request.session.get('mobilito_session_id'))
            session_object.end_timestamp = now
            session_object.pedestrian_count = number_of_pedestrians
            session_object.bicycle_count = number_of_bicycles
            session_object.motor_vehicle_count = \
                number_of_cars
            session_object.public_transport_count = \
                number_of_public_transports
            session_object.save()
        except Session.DoesNotExist as e:
            logger.error(
                f"Can't update a non-existing session, "
                f"user={request.user.email}, {e}")

        # Thank you page
        # request.session is used to fill the thank you page
        request.session['recording_duration_minutes'] = int(
            (
                datetime.now(timezone.utc)
                - session_object.start_timestamp
            ).total_seconds() // 60
        )
        request.session['number_of_pedestrians'] = number_of_pedestrians
        request.session['number_of_bicycles'] = number_of_bicycles
        request.session['number_of_cars'] = number_of_cars
        request.session['number_of_public_transports'] = \
            number_of_public_transports

        return HttpResponseRedirect(reverse('mobilito:thanks'))


class ThankYouView(TemplateView):
    template_name = 'mobilito/thanks.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        request.session.pop("address", None)
        request.session.pop("city", None)
        request.session.pop("postcode", None)
        request.session.pop("country", None)
        request.session.pop("mobilito_session_id", None)
        return super().get(request, *args, **kwargs)


def get_session_object(request: HttpRequest) -> Union[Session, None]:
    """Get the session object, convenience function."""
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
        event_type = request.POST.get('event_type').lower()
        if event_type == 'pedestrian':
            event_type = 'ped'
        elif event_type == 'bicycle':
            event_type = 'bike'
        elif event_type == 'motor-vehicle':
            event_type = 'car'
        elif event_type == 'public-transport':
            event_type = 'TC'
        if session_object:
            session_object.create_event(event_type)
            return HttpResponse(status=200)

        logger.error(f"{request.user.email} tried to create an event from a "
                     "non-existing session")

        return HttpResponse(status=200)

    if request.method == 'GET':
        return HttpResponse(status=403)
