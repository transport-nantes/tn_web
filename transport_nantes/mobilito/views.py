import io
import json
import logging
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
import matplotlib.image as mpimg
import matplotlib.text
import matplotlib.pyplot as plt
import numpy as np
import pickle
from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont
import random
import requests
from user_agents import parse
from typing import Union

import requests
from asso_tn.utils import make_timed_token, token_valid
from authentication.views import create_send_record
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import (Http404, HttpRequest, HttpResponse,
                         HttpResponseRedirect, JsonResponse)
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from asso_tn.utils import make_timed_token, token_valid

from authentication.views import create_send_record
from topicblog.models import SendRecordTransactionalAdHoc
from transport_nantes.settings import MAPS_API_KEY
from user_agents import parse

from mobilito.forms import AddressForm
from mobilito.models import (InappropriateFlag, MobilitoSession, MobilitoUser, Event)

logger = logging.getLogger("django")

#matplotlib.rcParams['font.family'] = 'Montserraat-Bold'
#matplotlib.rcParams['font.family'] = 'Montserraat'

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
                              'velos', 'transports-collectifs', ])

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
        hex_cookie = b64encode(pickle.dumps(pages_seen)).hex()
        signed_cookie = make_timed_token(string_key=hex_cookie, minutes=120)
        response.set_cookie(
            key=self.tutorial_cookie_name,
            value=signed_cookie,
            expires=datetime.now(timezone.utc) + timedelta(hours=2))

    def pages_seen(self, request) -> set:
        """Return the set of pages the user has seen.

        The set is based on the tutorial cookie, and so expires when
        it does.

        """
        if request.user.is_authenticated:
            mobilito_user = get_MobilitoUser(request)
            if mobilito_user.completed_tutorial_timestamp:
                return self.all_tutorial_pages
        signed_tutorial_cookie = request.COOKIES.get(
            self.tutorial_cookie_name, '')
        if not signed_tutorial_cookie:
            return set()
        tutorial_cookie, _ = token_valid(signed_tutorial_cookie)
        if tutorial_cookie:
            pages_seen: set = pickle.loads(b64decode(bytes.fromhex(tutorial_cookie)))
            return pages_seen
        # Cookie not valid, either too old or not generated by us.
        return set()

    def pages_to_see(self, request, this_page=None) -> set:
        """Return the set of pages the user must see.

        If the user is still required to view tutorial pages, return
        the set required.  If we are composing a tutorial page for the
        user, do not count it as needing to be seen, since it will
        have been see by the time it matters.

        """
        if request.user.is_authenticated:
            mobilito_user = get_MobilitoUser(request)
            if mobilito_user.completed_tutorial_timestamp:
                # User has seen all tutorial pages, nothing left to see.
                return set()
        return self.all_tutorial_pages - self.pages_seen(request) - set([this_page])

    def next_page_to_see(self, request, this_page=None) -> str:
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
            return ""


class MobilitoView(TemplateView):
    """Present Mobilito landing page.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # Need to set the boolean tutorial_done, to True if the user
        # has finished the tutorial, to False if not.
        tutorial_state = TutorialState()
        if tutorial_state.pages_to_see(request):
            context['tutorial_done'] = False
        else:
            context['tutorial_done'] = True
        return self.render_to_response(context)


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
        mobilito_session = MobilitoSession.objects.create(
            user=user,
            location=location,
            latitude=latitude,
            longitude=longitude,
            user_browser=str(user_agent),
            start_timestamp=datetime.now(timezone.utc),
        )
        self.request.session["mobilito_session_id"] = mobilito_session.id
        logger.info(
            f'{self.request.user.email} started mobilito_session {mobilito_session.id}')
        return context

    def get(self, request, *args, **kwargs):
        tutorial_state = TutorialState()
        if tutorial_state.pages_to_see(self.request):
            next_page = tutorial_state.next_page_to_see(request)
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
        # Update of associated mobilito_session
        try:
            mobilito_session: MobilitoSession = \
                MobilitoSession.objects.get(
                    id=request.session.get('mobilito_session_id'))
            mobilito_session.end_timestamp = now
            mobilito_session.pedestrian_count = number_of_pedestrians
            mobilito_session.bicycle_count = number_of_bicycles
            mobilito_session.motor_vehicle_count = \
                number_of_cars
            mobilito_session.public_transport_count = \
                number_of_public_transports
            mobilito_session.save()
            send_results(request, mobilito_session)
        except MobilitoSession.DoesNotExist as e:
            logger.error(
                f"Can't update a non-existing mobilito_session, "
                f"id={request.session.get('mobilito_session_id', '')}, "
                f"user={request.user.email}, {e}")

        # Thank you page
        # request.session is used to fill the thank you page
        request.session['recording_duration_minutes'] = int(
            (
                datetime.now(timezone.utc)
                - mobilito_session.start_timestamp
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


def get_mobilito_session(request: HttpRequest) -> Union[MobilitoSession, None]:
    """Get the mobilito_session object, convenience function."""
    try:
        mobilito_session = MobilitoSession.objects.get(
            id=request.session.get('mobilito_session_id'))
    except MobilitoSession.DoesNotExist as e:
        logger.error(
            f'{request.user.email} tried to get a non-existing '
            f'mobilito_session : {e}')
        mobilito_session = None
    return mobilito_session


def create_event(request: HttpRequest) -> HttpResponse:
    """Create a Mobilito event from a POST request"""
    if request.method == 'POST':
        mobilito_session = get_mobilito_session(request)
        event_type = request.POST.get('event_type').lower()
        if event_type == 'pedestrian':
            event_type = 'ped'
        elif event_type == 'bicycle':
            event_type = 'bike'
        elif event_type == 'motor-vehicle':
            event_type = 'car'
        elif event_type == 'public-transport':
            event_type = 'TC'
        if mobilito_session:
            mobilito_session.create_event(event_type)
            return HttpResponse(status=200)

        logger.error(f"{request.user.email} tried to create an event from a "
                     "non-existing mobilito_session")

        return HttpResponse(status=200)

    if request.method == 'GET':
        return HttpResponse(status=403)


def send_results(request: HttpRequest, mobilito_session: MobilitoSession) -> None:
    """Send mobilito_session's results by email to user"""
    logger.info(f'Sending mobilito_session results to {request.user.email}')
    try:
        logger.info(f'MobilitoSession id : {mobilito_session.id}')
        logger.info("Creating send record ...")
        send_record = create_send_record(request.user.email)
        custom_email = prepare_email(request, mobilito_session, send_record)
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
        request: HttpRequest, mobilito_session: MobilitoSession,
        send_record: SendRecordTransactionalAdHoc) -> EmailMultiAlternatives:
    """Prepare the email to be sent"""
    logger.info(f'Preparing email for {mobilito_session.user.user.email}')
    template = "mobilito/result_email.html"
    context = {
        'request': request,
        'mobilito_session': mobilito_session,
        'nb_pedestrians': mobilito_session.pedestrian_count,
        'nb_bicycles': mobilito_session.bicycle_count,
        'nb_cars': mobilito_session.motor_vehicle_count,
        'nb_TC': mobilito_session.public_transport_count,
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


def get_MobilitoUser(request) -> Union[MobilitoUser, None]:
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


class MobilitoSessionSummaryView(TemplateView):
    """Display the details of a Mobilito Session"""
    model = MobilitoSession
    template_name = 'mobilito/mobilito_session_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_sha1 = self.kwargs.get('session_sha1')
        requested_mobilito_session = get_object_or_404(
            MobilitoSession, session_sha1=session_sha1)
        context["mobilito_session"] = requested_mobilito_session
        user = self.request.user if self.request.user.is_authenticated else None
        reporter_tn_session_id = self.request.session.get('tn_session')

        user_has_reported_this_session = InappropriateFlag.objects.filter(
            Q(reporter_user=user)
            | Q(reporter_tn_session_id=reporter_tn_session_id),
            session=requested_mobilito_session,
        ).exists()

        context["user_has_reported_this_session"] = user_has_reported_this_session
        return context

    def check_view_permission(self, obj: MobilitoSession) -> None:
        """Check if the user has permission to view the mobilito session

        Only the session creator and authorised users can see the
        mobilito session if it's unpublished.

        """

        if obj.published is False:
            mobilito_user = get_MobilitoUser(self.request)
            if (not self.request.user.has_perm('mobilito.mobilito_session.view_session')
                    and mobilito_user != obj.user):
                raise Http404

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = self.get_context_data(**kwargs)
        self.check_view_permission(context["mobilito_session"])
        return self.render_to_response(context)


fonts_inited = False

def init_brand_font():
    """Initialise our brand font.

    This function may be a bit of a hack.

    """
    global fonts_inited
    if not fonts_inited:
        logger.info('Initing fonts.')
        fontdir="open_graph/base_images/Montserrat/"
        font_manager.findSystemFonts(fontdir)
        for font in font_manager.findSystemFonts(fontdir):
            font_manager.fontManager.addfont(font)
        matplotlib.rcParams['font.family'] = "Montserrat"
        fonts_inited = True

def mobilito_session_timeseries_image(request, session_sha1):
    """Generate a time series visualisation of a Mobilito session.

    The point of this graphic is to visualise the time evolution of
    traffic in the four modes we measure, giving an idea of density
    over time of each mode.

    On a web page we'll (eventually) use d3 to render these images, as
    it's lighter and responsive.  But in email, a PNG works far
    better, in the sense that d3 won't render in many an email client.

    This needs to be localised to French.  And most of the
    labels/titles are place holders for now.

    """
    mobilito_session = get_object_or_404(
        MobilitoSession, session_sha1=session_sha1)
    events = Event.objects.filter(mobilito_session=mobilito_session)
    # Specify our brand font.
    #### This will only work in dev due to path name.
    tn_font_path = 'open_graph/base_images/Montserrat/Montserrat-Bold.otf'
    tn_font_size = 150
    tn_font = ImageFont.truetype(tn_font_path, tn_font_size)
    scatter_map = {
        Event.EventTypes.PEDESTRIAN: 0,
        Event.EventTypes.BICYCLE: 1,
        Event.EventTypes.MOTOR_VEHICLE: 2,
        Event.EventTypes.PUBLIC_TRANSPORT: 3,
    }

    init_brand_font()
    mobilitains_light_blue = (91./255, 194./255, 231./255)
    mobilitains_dark_blue = (67./255, 82./255, 110./255)
    mobilitains_gray = (219./255, 227./255, 235./255)
    mobilitains_red = (250./255, 70./255, 22./255)
    mobilitains_maroon = (128./255, 105./255, 102./255)

    img_walking = mpimg.imread("mobilito/static/mobilito/images/ped-icon-small.png")
    img_bicycle = mpimg.imread("mobilito/static/mobilito/images/bike-icon-small.png")
    img_car = mpimg.imread("mobilito/static/mobilito/images/car-icon-small.png")
    img_tc = mpimg.imread("mobilito/static/mobilito/images/tc-icon-small.png")
    image_icons = [img_walking, img_bicycle, img_car, img_tc]
    intermode_vertical = 1
    vertical_jitter = .3
    event_timestamps = [an_event.timestamp for an_event in events]
    min_timestamp = min(event_timestamps)
    # Plot four invisible points on the center lines in order to make
    # the plot register correctly, even if some modes have no data.
    x_scatter_points = [min_timestamp] * 4 + event_timestamps
    y_scatter_points = [0, 1, 2, 3] + \
        [intermode_vertical * scatter_map[an_event.event_type] \
         + vertical_jitter * (random.random() - .5)
         for an_event in events]
    point_colors = [mobilitains_dark_blue] * 4 + [mobilitains_light_blue] * len(events)

    fig, ax = plt.subplots(figsize=(8,5), dpi=100)

    #ax.scatter(x_scatter_points, y_scatter_points, s=10, c=(mobilitains_gray))
    # print('tick locs', ax.get_xaxis().get_ticklocs())
    # print('major ticks', ax.get_xaxis().get_major_ticks())
    # print('extents', ax.get_xaxis().get_major_ticks()[0].get_clip_box().extents)

    yaxis_0 = ax.get_yaxis()
    tick_locs_0 = yaxis_0.get_ticklocs()
    #ax.set_clip_on(False)

    # Place a new axes for each image where we want the image.
    # (x, y, width, height).
    # Then remove ticks and box before rendering.
    horizontal_offset = 0.02
    base_height = 0.17
    incr_height = 0.21

    walk_icon = fig.add_axes([horizontal_offset, base_height + 0 * incr_height, 0.05, 0.05])
    walk_icon.set_axis_off()
    walk_icon.imshow(img_walking, aspect="equal")

    bicycle_icon = fig.add_axes([horizontal_offset, base_height + 1 * incr_height, 0.05, 0.05])
    bicycle_icon.set_axis_off()
    bicycle_icon.imshow(img_bicycle, aspect="equal")

    car_icon = fig.add_axes([horizontal_offset, base_height + 2 * incr_height, 0.05, 0.05])
    car_icon.set_axis_off()
    car_icon.imshow(img_car, aspect="equal")

    tc_icon = fig.add_axes([horizontal_offset, base_height + 3 * incr_height, 0.05, 0.05])
    tc_icon.set_axis_off()
    tc_icon.imshow(img_tc, aspect="equal")

    ax.scatter(x_scatter_points, y_scatter_points, s=10, c=point_colors)
    ax.set_facecolor(mobilitains_dark_blue)

    # The concise data formatter isn't useful but it's clear.
    # So this needs work.
    ax.xaxis.set_major_formatter(
        mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.tick_params(axis='x', colors=mobilitains_gray)

    ax.set_xlabel("Temps", color=mobilitains_gray)
    ax.set_title("Trafic par mode", color=mobilitains_gray)

    ax.set_yticks([])
    ax.spines['bottom'].set_color(mobilitains_gray)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

    fig.set_facecolor(mobilitains_dark_blue)
    fig.tight_layout(pad=2.0)
    buf = io.BytesIO()
    fig.set_size_inches(10, 5)
    fig.savefig(buf, format='png', dpi=100)
    plt.close()
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response


def mobilito_session_fraction_image(request, session_sha1):
    """Generate an image of the eco fraction of a Mobilito session.

    The point of this graphic is to visualise the fraction of
    pedestrian and bicycle traffic compard to car traffic.  It's
    objective is purely to visualise a fraction, a / b.

    On a web page we'll (eventually) use d3 to render these images, as
    it's lighter and responsive.  But in email, a PNG works far
    better, in the sense that d3 won't render in many an email client.

    This needs to be localised to French.  And most of the
    labels/titles are place holders for now.

    """
    mobilito_session = get_object_or_404(
        MobilitoSession, session_sha1=session_sha1)
    events = Event.objects.filter(mobilito_session=mobilito_session)
    # Specify our brand font.
    #### This will only work in dev due to path name.
    tn_font_path = 'open_graph/base_images/Montserrat/Montserrat-Bold.otf'
    tn_font_size = 150
    tn_font = ImageFont.truetype(tn_font_path, tn_font_size)
    scatter_map = {
        Event.EventTypes.PEDESTRIAN: 0,
        Event.EventTypes.BICYCLE: 1,
        Event.EventTypes.MOTOR_VEHICLE: 2,
        Event.EventTypes.PUBLIC_TRANSPORT: 3,
    }

    img_walking = mpimg.imread("mobilito/static/mobilito/images/ped-icon-small.png")
    img_bicycle = mpimg.imread("mobilito/static/mobilito/images/bike-icon-small.png")
    img_car = mpimg.imread("mobilito/static/mobilito/images/car-icon-small.png")
    img_tc = mpimg.imread("mobilito/static/mobilito/images/tc-icon-small.png")
    image_icons = [img_walking, img_bicycle, img_car, img_tc]

    init_brand_font()
    mobilitains_light_blue = (91./255, 194./255, 231./255)
    mobilitains_dark_blue = (67./255, 82./255, 110./255)
    mobilitains_gray = (219./255, 227./255, 235./255)
    mobilitains_red = (250./255, 70./255, 22./255)
    mobilitains_maroon = (128./255, 105./255, 102./255)

    fig, ax = plt.subplots(figsize=(3,3), dpi=100)

    modal_values = [mobilito_session.pedestrian_count,
                    mobilito_session.bicycle_count,
                    mobilito_session.motor_vehicle_count,
                    mobilito_session.public_transport_count,]
    modal_colors = [mobilitains_light_blue,
                    mobilitains_light_blue,
                    mobilitains_red,
                    mobilitains_maroon,]
    modal_explosion = [.01] * 4
    pie = ax.pie(modal_values,
                 colors=modal_colors,
                 explode=modal_explosion)
    pie_text = pie[1]
    #print(pie_text)
    #print(pie_text[0].get_position())

    # Bug: these axes are being positioned in the coordinate system of
    # the figure rather than relative to the pie axes.
    walk_icon = fig.add_axes([pie_text[0].get_position()[0],
                              pie_text[0].get_position()[1],
                              0.05, 0.05])
    walk_icon.set_axis_off()
    walk_icon.imshow(img_walking, aspect="equal")

    bicycle_icon = fig.add_axes([pie_text[1].get_position()[0],
                                 pie_text[1].get_position()[1],
                                 0.05, 0.05], zorder=10)
    bicycle_icon.set_axis_off()
    bicycle_icon.imshow(img_bicycle, aspect="equal")

    car_icon = fig.add_axes([pie_text[2].get_position()[0],
                             pie_text[2].get_position()[1],
                             0.05, 0.05],
                            zorder=-1,
                            transform=ax.transAxes)
    car_icon.set_axis_off()
    car_icon.imshow(img_car, aspect="equal")

    tc_icon = fig.add_axes([pie_text[3].get_position()[0],
                            pie_text[3].get_position()[1],
                            0.05, 0.05])
    tc_icon.set_axis_off()
    tc_icon.imshow(img_tc, aspect="equal")

    bike_ped_share = (100.0 * (mobilito_session.pedestrian_count +
                               mobilito_session.bicycle_count)
                      / (mobilito_session.pedestrian_count +
                         mobilito_session.bicycle_count +
                         mobilito_session.motor_vehicle_count))
    ax.set_title(f"{bike_ped_share:.0f} % piétons et vélos",
                 color=mobilitains_gray)

    fig.set_facecolor(mobilitains_dark_blue)
    fig.tight_layout(pad=2.0)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close()
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response


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


@csrf_protect
def flag_session(request: HttpRequest, **kwargs) -> HttpResponse:
    """Flag a session as inappropriate"""

    def get_client_ip(request):
        """Remove dependence on ipware module.

        We should stop relying on remote ip address unless we can
        document a real interest in storing it.  It's questionnable
        from a GDPR standpoint, it's 100% unactionnable for us, and we
        don't have engineering resources to confirm that we're
        reliably recovering remote ip and not a proxy ip along the
        route (or a hacked ip).

        https://www.djangoproject.com/weblog/2009/jul/28/security/#secondary-issue

        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None

        session_sha1 = kwargs['session_sha1']
        try:
            # In the event that somehow, in spite of CSRF protection, a user
            # tries to flag a session that doesn't exist, we don't want to
            # crash the app, so we catch the exception, log it and return a 404
            session_object = get_object_or_404(
                MobilitoSession, session_sha1=session_sha1)
        except Http404:
            logger.error(f"{user or 'Anonymous User'} tried to flag a "
                         f"non-existing session : {session_sha1}")
            raise Http404

        _, created = InappropriateFlag.objects.get_or_create(
            session=session_object,
            reporter_user=user,
            reporter_tn_session_id=request.session.get('tn_session'),
            defaults={
                'session': session_object,
                'reporter_user': user,
                'reporter_tn_session_id': request.session.get('tn_session'),
                'report_details': request.POST.get('report-abuse-text'),
            })
        if created:
            logger.info(f"{user or 'Anonymous User'} flagged session "
                        f"{session_object.id}")
        else:
            logger.info(f"{user or 'Anonymous User'} tried to flag session "
                        f"{session_object.id} but they already flagged it")

        return HttpResponse(status=200)

    if request.method == 'GET':
        return HttpResponse(status=405)
