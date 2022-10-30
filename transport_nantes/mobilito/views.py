from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
import json
import logging
import pickle
import requests
from user_agents import parse
from typing import Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import (Http404, HttpRequest, HttpResponse,
                         HttpResponseRedirect, JsonResponse,)
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from asso_tn.utils import make_timed_token, token_valid

from mobilito.models import MobilitoUser, Session
from mobilito.forms import AddressForm
from authentication.views import create_send_record
from topicblog.models import SendRecordTransactionalAdHoc
from transport_nantes.settings import MAPS_API_KEY

logger = logging.getLogger("django")


class TutorialState:
    """Track tutorial pages viewed.

    We track tutorial page views with a short-timeout cookie that
    represents a set of tutorial pages seen.  If the cookie is absent
    (and the user is not authenticated with a record of having
    completed the tutorial), then the set of pages seen is empty.
    Once the user has seen all the pages, and only then, we permit
    recording sessions.

    Once the user is authenticated and has completed all pages, we
    persist that fact to the user record.

    Note that we don't persist tutorial views for authenticated users
    who have only seen some tutorial records.  They depend on the
    short timeout cookie.  Once they have seen all pages, we persist
    the fact that they are done.

    Similarly, unauthenticated users who don't authenticate will time
    out their tutorial views with the cookie and so have to review the
    tutorial.

    The tutorial is intended to be short enough that none of this
    should be particularly bothersome.  Our goal is simply to make
    sure everyone who records has some chance of knowing what our
    expectations are, what the different buttons mean.

    """
    tutorial_cookie_name = 'mobilito_tutorial'
    all_tutorial_pages = set(['presentation', 'pietons', 'voitures',
                              'velos', 'transports-collectifs',])

    def default_page(self) -> str:
        """Return the tutorial page to view if no page requested."""
        return "presentation"

    def canonical_page(self, page_name) -> str:
        """Return a valid tutorial page name."""
        if page_name in self.all_tutorial_pages:
            return page_name
        return self.default_page()

    def persist_pages_seen(self, response, pages_seen) -> None:
        """Persist the tutorial cookie."""
        response.set_cookie(
            key=self.tutorial_cookie_name,
            value=b64encode(pickle.dumps(pages_seen)).hex(),
            expires=datetime.now(timezone.utc) + timedelta(hours=2))

    def pages_seen(self, request) -> set:
        """Return the set of pages the user has seen.

        The set is based on the tutorial cookie, and so expires when
        it does.

        """
        if 'user' in request and request.user.is_authenticated:
            mobilito_user = get_MobilitoUser(request)
            if mobilito_user.completed_tutorial_timestamp:
                return all_tutorial_pages
        tutorial_cookie = request.COOKIES.get(
            self.tutorial_cookie_name, '')
        if not tutorial_cookie:
            return set()
        pages_seen: set = pickle.loads(b64decode(bytes.fromhex(tutorial_cookie)))
        return pages_seen

    def pages_to_see(self, request, this_page=None) -> set:
        """Return the set of pages the user must see.

        If the user is still required to view tutorial pages, return
        the set required.  If we are composing a tutorial page for the
        user, do not count it as needing to be seen, since it will
        have been see by the time it matters.

        """
        if 'user' in request and request.user.is_authenticated:
            mobilito_user = get_MobilitoUser(request)
            if mobilito_user.completed_tutorial_timestamp:
                # User has seen all tutorial pages, nothing left to see.
                return set()
        return self.all_tutorial_pages - self.pages_seen(request) - set([this_page])

    def next_page_to_see(self, request, this_page) -> str:
        """Return the next tutorial page to visit.

        If the user must still see some tutorial pages, this function
        will provide one to visit next.  We maintain no concept of the
        order in which visitors _should_ visit pages, and so this
        function is free to choose any non-visited tutorial page to
        propose as the next page to visit.

        If we are currently composing a tutorial page, do not consider
        it as unseen and so a potential next page.
        Cf. pages_to_see().

        If the user has seen all tutorial pages, return None.

        """
        try:
            return next(iter(self.pages_to_see(request, this_page)))
        except StopIteration:
            return None


class MobilitoView(TemplateView):
    """Present Mobilito landing page.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/index.html'


class TutorialView(TemplateView):
    """Present the tutorial.
    """

    template_name = 'mobilito/tutorial.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # It's modestly wasteful to set the tutorial cookie for auth'd
        # users who have completed the tutorial, but it's manifestly
        # easier to express.  We'll ingore the cookie if necessary.
        tutorial_state = TutorialState()
        pages_seen = tutorial_state.pages_seen(self.request)
        this_page = self.kwargs.get("tutorial_page", None)
        if this_page:
            pages_seen.add(this_page)
        tutorial_state.persist_pages_seen(response, pages_seen)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tutorial_state = TutorialState()
        this_page = tutorial_state.canonical_page(
            kwargs.get('tutorial_page', None))
        self.template_name = f'mobilito/tutorial_{this_page}.html'

        next_page = tutorial_state.next_page_to_see(self.request, this_page)
        if next_page:
            context["the_next_page"] = next_page
        return context


class AddressFormView(LoginRequiredMixin, FormView):
    """Present the address form.
    The form is optional to fill.
    """

    template_name = 'mobilito/geolocation_form.html'
    form_class = AddressForm
    success_url = reverse_lazy('mobilito:recording')

    def get(self, request, *args, **kwargs):
        tutorial_state = TutorialState()
        if tutorial_state.pages_to_see(self.request):
            next_page = tutorial_state.next_page_to_see(request)
            return HttpResponseRedirect(
                reverse('mobilito:tutorial',
                        kwargs={'tutorial_page': next_page}))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session["location"] = form.cleaned_data['location']
        self.request.session["latitude"] = form.cleaned_data['latitude']
        self.request.session["longitude"] = form.cleaned_data['longitude']
        logger.info(
            f'{self.request.user.email} filled address form.\n'
            f'Address saved: {self.request.session["location"]}')
        return super().form_valid(form)


class RecordingView(LoginRequiredMixin, TemplateView):
    template_name = 'mobilito/recording.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super(TemplateView, self).get_context_data(**kwargs)
        location = self.request.session.get('location')
        latitude = self.request.session.get('latitude')
        longitude = self.request.session.get('longitude')
        user_agent = parse(self.request.META.get('HTTP_USER_AGENT'))
        user = MobilitoUser.objects.get_or_create(
            user=self.request.user)[0]
        session_object = Session.objects.create(
            user=user,
            location=location,
            latitude=latitude,
            longitude=longitude,
            user_browser=str(user_agent),
            start_timestamp=datetime.now(timezone.utc),
        )
        self.request.session["mobilito_session_id"] = session_object.id
        logger.info(
            f'{self.request.user.email} started session {session_object.id}')
        return context

    def get(self, request, *args, **kwargs):
        tutorial_state = TutorialState()
        if tutorial_state.pages_to_see(self.request):
            next_pag = tutorial_state.next_page_to_see(request)
            return HttpResponseRedirect(
                reverse('mobilito:tutorial',
                        kwargs={'tutorial_page': next_page}))
        return super().get(request, *args, **kwargs)

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
            send_results(request, session_object)
        except Session.DoesNotExist as e:
            logger.error(
                f"Can't update a non-existing session, "
                f"id={request.session.get('mobilito_session_id', '')}, "
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

#    def get_context_data(self, **kwargs) -> dict:
#        context = super(TemplateView, self).get_context_data(**kwargs)
#        return context


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


def send_results(request: HttpRequest, session_object: Session) -> None:
    """Send session's results by email to user"""
    logger.info(f'Sending session results to {request.user.email}')
    try:
        logger.info(f'Session id : {session_object.id}')
        logger.info("Creating send record ...")
        send_record = create_send_record(request.user.email)
        custom_email = prepare_email(request, session_object, send_record)
        logger.info(f'Sending email to {request.user.email}')
        custom_email.send(fail_silently=False)
        logger.info(f'Email sent to {request.user.email}')
        send_record.handoff_time = datetime.now(timezone.utc)
        send_record.save()
    except Exception as e:
        # We don't really know that this is why we are here.
        # We've caught a generic exception.
        logger.error(f'Error sending email to {request.user.email} : {e}')
        send_record.status = "FAILED"
        send_record.save()


def prepare_email(
        request: HttpRequest, session_object: Session,
        send_record: SendRecordTransactionalAdHoc) -> EmailMultiAlternatives:
    """Prepare the email to be sent"""
    logger.info(f'Preparing email for {session_object.user.user.email}')
    template = "mobilito/result_email.html"
    context = {
        'request': request,
        'session_object': session_object,
        'nb_pedestrians': session_object.pedestrian_count,
        'nb_bicycles': session_object.bicycle_count,
        'nb_cars': session_object.motor_vehicle_count,
        'nb_TC': session_object.public_transport_count,
    }

    html_message = render_to_string(template, context=context, request=request)

    values_to_pass_to_ses = {
        "send_record class": send_record.__class__.__name__,
        "send_record id": str(send_record.id),
    }
    comments_header = json.dumps(values_to_pass_to_ses)
    headers = {
        "X-SES-CONFIGURATION-SET": settings.AWS_CONFIGURATION_SET_NAME,
        "Comments": comments_header}
    email = EmailMultiAlternatives(
        subject="Les résultats de votre session Mobilito sont là !",
        body=render_to_string(template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[send_record.recipient.email],
        headers=headers,
    )
    email.attach_alternative(html_message, "text/html")

    if settings.ROLE == "dev":
        logger.info(f"Sending this email to {send_record.recipient.email}:\n\n"
                    f"{render_to_string(template, context)}")
    return email


def get_MobilitoUser(request):
    """Get the MobilitoUser object for the current user.

    If the user is authenticated, return the related MobilitoUser
    object, creating it if necessary.

    """
    if request.user.is_authenticated:
        user, created = MobilitoUser.objects.get_or_create(
            user=request.user,
            defaults={
                "user": request.user,
                'first_time': True,
            })
        user: MobilitoUser
        created: bool
        if created:
            logger.info(f"Created MobilitoUser {user}")
    else:
        user = None

    return user


class SessionSummaryView(TemplateView):
    """Display the details of a Mobilito Session"""
    model = Session
    template_name = 'mobilito/session_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_sha1 = self.kwargs.get('session_sha1')
        requested_session = get_object_or_404(Session, session_sha1=session_sha1)
        context["mobilito_session"] = requested_session
        return context

    def check_view_permission(self, obj: Session) -> None:
        """Check if the user has permission to view the session

        Only author and authorised users can see the session if it's unpublished
        """

        if obj.published is False:
            mobilito_user = get_MobilitoUser(self.request)
            if (not self.request.user.has_perm('mobilito.session.view_session')
                    and mobilito_user != obj.user):
                raise Http404

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        self.check_view_permission(context["mobilito_session"])
        return self.render_to_response(context)


class ReverseGeocodingView(View):

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Return the reverse-geocoded address from a lat,lng tuple"""
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if lat and lng:
            url = (
                "https://maps.googleapis.com/maps/api/geocode/json?"
                f"latlng={lat},{lng}&key={MAPS_API_KEY}"
            )
            response = requests.get(url)
            return JsonResponse(response.json())

        return HttpResponse(status=400)
