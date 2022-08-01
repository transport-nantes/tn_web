from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
import json
import logging
import pickle
from user_agents import parse
from typing import Union

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from asso_tn.utils import make_timed_token, token_valid

from mobilito.models import MobilitoUser, Session
from mobilito.forms import AddressForm
from authentication.views import create_send_record
from topicblog.models import SendRecordTransactionalAdHoc

logger = logging.getLogger("django")


class MobilitoView(TemplateView):
    """Present Mobilito landing page.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/index.html'


class TutorialView(TemplateView):
    """Present the tutorial.
    """

    template_name = 'mobilito/tutorial.html'
    tutorial_cookie_name = 'mobilito_tutorial'

    # Map each tutorial page name to the datetime before which the
    # user is assumed not to have see it (i.e., the page's last
    # modification or its creation or just we want to show it again).
    last_mod_date = datetime(
        year=2022, month=8, day=3, tzinfo=timezone.utc)
    all_tutorial_pages = {
        'presentation': {"last_modified": last_mod_date},
        'pietons': {"last_modified": last_mod_date},
        'voitures': {"last_modified": last_mod_date},
        'velos': {"last_modified": last_mod_date},
        'transports-collectifs': {"last_modified": last_mod_date},
    }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        tutorial_cookie_value = context.get('mobilito_tutorial', '')
        response = self.render_to_response(context)
        response.set_cookie(
            key='mobilito_tutorial',
            value=tutorial_cookie_value,
            expires=datetime.now(timezone.utc) + timedelta(hours=2))

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        this_page = kwargs.get('tutorial_page', 'presentation')
        if this_page not in self.all_tutorial_pages:
            # Trying to access a tutorial page that doesn't exist.
            raise Http404()
        context['active_page'] = this_page
        self.template_name = f'mobilito/tutorial_{this_page}.html'

        pages_seen = self.get_seen_pages_from_cookie()
        if this_page not in pages_seen:
            pages_seen.append(this_page)
        pickled_pages_seen = pickle.dumps(pages_seen)
        pages_seen = make_timed_token(
            string_key=b64encode(pickled_pages_seen).decode(),
            minutes=120)

        # Store the list in context to then be added to the response.
        context['mobilito_tutorial'] = pages_seen

        next_page = self.get_next_tutorial_page()
        if next_page:
            context["the_next_page"] = next_page
        else:
            if self.request.user.is_authenticated:
                user = get_MobilitoUser(self)
                user.completed_tutorial_timestamp = datetime.now(
                    timezone.utc)
                user.first_time = False
                user.save()
            context["the_next_page"] = self.not_this_page(this_page)

        return context

    def get_seen_pages_from_cookie(self) -> list:
        """Return the list of pages seen from the cookie."""
        pages_seen = self.request.COOKIES.get(
            self.tutorial_cookie_name, '')
        if pages_seen:
            pickled_pages_seen, _ = token_valid(pages_seen)
            if pickled_pages_seen:
                pages_seen_list: list = pickle.loads(
                    b64decode(pickled_pages_seen))
                return pages_seen_list
            else:
                logger.info(
                    "Invalid token provided for mobilito "
                    f"tutorial : {pages_seen}")
        return []

    def get_pages_to_visit(self) -> list:
        """Return the list of pages to visit.

        This is used by the bottom arrow to redirect to the next page.
        """
        # This returns a list of pages visited.
        pages_seen: list = self.get_seen_pages_from_cookie()
        if self.request.user.is_authenticated:
            user = get_MobilitoUser(self)
            completed_tutorial_timestamp = user.completed_tutorial_timestamp
        else:
            completed_tutorial_timestamp = datetime(
                year=2022, month=8, day=3, tzinfo=timezone.utc)
        pages_to_visit = [page for page, last_mod_date
                          in self.all_tutorial_pages.items()
                          if page not in pages_seen
                          and completed_tutorial_timestamp
                          < last_mod_date["last_modified"]]
        return pages_to_visit

    def get_next_tutorial_page(self) -> str:
        """Return the name of the next tutorial page to visit.

        This is used for the forward arrow.  Return None if the user
        has seen all tutorial pages.
        """
        pages_to_visit = self.get_pages_to_visit()
        if pages_to_visit:
            return pages_to_visit[0]
        return None

    def not_this_page(self, this_page) -> str:
        """Return the next tutorial page, if all pages have been visited.
        """
        possible_pages = list(self.all_tutorial_pages.keys())
        index_of_this_page = possible_pages.index(this_page)
        if index_of_this_page == len(possible_pages) - 1:
            return possible_pages[0]
        return possible_pages[index_of_this_page + 1]


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
        try:
            send_results(request)
        except Exception as e:
            logger.error(
                f"Can't send email, user={request.user.email}, {e}")
        else:
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


def send_results(request: HttpRequest) -> None:
    """Send session's results by email to user"""
    logger.info(f'Sending session results to {request.user.email}')
    session_object = get_session_object(request)
    if session_object:
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

    return email


def get_MobilitoUser(self: Union[TemplateView, FormView]) -> Union[MobilitoUser, None]:
    """Get the MobilitoUser object for the current user"""
    if self.request.user.is_authenticated:
        user, created = MobilitoUser.objects.get_or_create(
            user=self.request.user,
            defaults={
                "user": self.request.user,
                'first_time': True,
            })
        user: MobilitoUser
        created: bool
        if created:
            logger.info(f"Created MobilitoUser {user}")
    else:
        user = None

    return user
