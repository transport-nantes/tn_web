from datetime import date, datetime, timezone
import logging
import json
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.crypto import get_random_string

from django.views.generic.edit import FormView
from django.core.mail import EmailMultiAlternatives
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import TemplateView

from authentication.forms import (EmailLoginForm, PasswordLoginForm,
                                  UserUpdateForm, ProfileUpdateForm)
from asso_tn.utils import make_timed_token, token_valid
from topicblog.models import SendRecordTransactional

"""
A quick note on the captcha:

1.  We should monitor it to know how often entities fail and how many
    attempts it requires to succeed.

2.  We should probably rate-limit the ability to response to captcha
    challenges.

3.  This article suggests that machines have become so good at
    responding to captchas that more human techniques are required.
    It proposes "add one to digits" as a test.  (This is consistent
    with the evolution of Google's recaptcha.)

    https://starcross.dev/blog/6/customising-django-simple-captcha/

4.  We don't use Google's recaptcha because we'd like to minimise data
    leaks to third parties, especially to GAFAs.

"""

logger = logging.getLogger("django")


def redirect_to_password_login(email, remember_me):
    """Helper function to redirect user to password login page.

    Return an HttpResponse.
    """
    token = make_timed_token(email, 1, remember_me)
    return redirect(
        reverse('authentication:password_login',
                kwargs={'token': token}))


class LoginView(FormView):
    template_name = "authentication/login.html"
    form_class = EmailLoginForm

    def form_valid(self, form):
        logger.info('form_valid')
        email = form.cleaned_data["email"]
        remember_me = form.cleaned_data["remember_me"]
        logger.info(f"{email} loggin request.")
        try:
            user = User.objects.get(email=email)
            authenticates_by_email = user.profile.authenticates_by_mail
        except User.DoesNotExist:
            logger.info(f"New user : Creation of user account for {email}")
            user = User()
            user.email = email
            user.username = get_random_string(length=20)
            user.set_unusable_password()
            user.save()
            authenticates_by_email = True
        if authenticates_by_email:
            logger.info(f"Sending email to {email}")
            try:
                send_activation(self.request, email, remember_me)
            except Exception as e:
                logger.error(f"Error sending activation email to {email}: {e}")
            return render(self.request,
                          'authentication/account_activation_sent.html') # noqa
        else:
            logger.info("Requesting password.")
            return redirect_to_password_login(email, remember_me)


class PasswordLoginView(FormView):
    template_name = "authentication/password_login.html"
    form_class = PasswordLoginForm

    def get(self, *args, **kwargs):
        token = self.kwargs.get('token', '')
        if not token:
            # No replays allowed.
            logger.info("Password login request without token.")
            return redirect(reverse('authentication:login'))
        email, remember_me = token_valid(token)
        if email is None:
            logger.info("Invalid password login token.")
            return redirect(reverse('authentication:login'))
        self.initial["email"] = email
        self.initial["remember_me"] = bool(remember_me)
        return super().get(*args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        remember_me = form.cleaned_data["remember_me"]
        user_by_email = User.objects.get(email=email)
        user = auth.authenticate(username=user_by_email.username,
                                 password=form.cleaned_data["password"])
        if user is None:
            # By doing a new redirect, we let the user have more time.
            # Otherwise the token would eventually time out.
            return redirect_to_password_login(email, remember_me)
        auth.login(self.request, user)
        # Set session cookie expiration to session duration if
        # "False" otherwise for 30 days
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(60*60*24*30)
        return redirect("/")


def send_activation(request, email, remember_me):
    """Send user an activation/login link.

    In fact, the user may not exist yet.  New users we create after
    they respond to the email link.

    The caller should then redirect to / render a template letting the
    user know the mail is on its way, since the redirect is a GET.

    """
    try:
        send_record = create_send_record(email)
        custom_email = prepare_email(email, request, send_record)
        logger.info(f"Sending activation email to {email}")
        custom_email.send(fail_silently=False)
        logger.info(f"Activation email sent to {email}")
        send_record.handoff_time = datetime.now(timezone.utc)
        send_record.save()
    except Exception as e:
        logger.error(f"Error while sending mail to {email} : {e}")
        send_record.status = "FAILED"
        send_record.save()


def create_send_record(email: str) -> SendRecordTransactional:
    """Create a SendRecordTransactional for the given email."""
    try:
        recipient = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.info("No user for email {}".format(email))
        recipient = None
    send_record = SendRecordTransactional.objects.create(
        recipient=recipient)
    return send_record


def prepare_email(email: str, request: HttpRequest,
                  send_record: SendRecordTransactional) \
        -> EmailMultiAlternatives:
    """Create a sendable Email object"""
    template = 'authentication/account_activation_email.html'
    next_url = request.GET.get('next', str())
    context = {
        "request": request,
        "token": make_timed_token(email, 20),
        "next_url": next_url,
        "host": get_current_site(request).domain,
    }
    html_message = render_to_string(template, context=context, request=request)
    # AWS SES reads the headers to check the presence of a configuration set.
    # If one is found, the configuration set allows notifications
    # regarding the email to be sent to the endpoints set in AWS (i.e. emails,
    # https, etc ...).
    # Depending on the event received (i.e. Bounce, delivery, rejected...),
    # different endpoints can be notified.
    # Without this header, the email is sent but no notification will be sent
    # to the endpoints.
    values_to_pass_to_ses = {
        "send_record class": send_record.__class__.__name__,
        "send_record id": str(send_record.id),
    }
    # The Comments header is a non structured header that allows us to pass
    # arbitrary data to SES. See https://www.ietf.org/rfc/rfc0822.txt
    # for more information.
    # This header field accepts text as value, so we create a string from a
    # dictionary.
    comments_header = json.dumps(values_to_pass_to_ses)
    headers = {
        "X-SES-CONFIGURATION-SET": settings.AWS_CONFIGURATION_SET_NAME,
        "Comments": comments_header}
    email = EmailMultiAlternatives(
        subject="Votre lien Mobilitains, comme promis",
        body=render_to_string(template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        headers=headers,
    )
    email.attach_alternative(html_message, 'text/html')

    return email


class ActivationLoginView(TemplateView):

    template_name = "authentication/mail_confirmed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get('token', '')
        email, remember_me = token_valid(token)
        self.next_url = self.request.GET.get('next', str())
        if email is None:
            logger.info(f"Invalid token : {token}")
            self.template_name = \
                'authentication/account_activation_invalid.html'
            return context

        user = User.objects.filter(email=email).first()
        if user is None:
            logger.info(f"Creation of user account for {email}")
            user = User()
            user.email = email
            user.username = get_random_string(length=20)
            user.set_unusable_password()
            user.save()

        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        auth.login(self.request, user)
        # Set session cookie expiration to session duration if "False"
        # otherwise for 30 days
        if remember_me == "False":
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(60*60*24*30)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if getattr(self, 'next_url', None):
            return HttpResponseRedirect(self.next_url)
        return self.render_to_response(context)


class DeauthView(LogoutView):
    """Log out the user.
    Renders the home page
    """
    next_page = "/"


class ProfileView(TemplateView, LoginRequiredMixin):

    template_name = "authentication/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["u_form"] = UserUpdateForm(instance=self.request.user)
        context["p_form"] = ProfileUpdateForm(
            instance=self.request.user.profile)

        return context

    def post(self, request, *args, **kwargs):

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES,
                                   instance=request.user.profile)
        success = False
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            success = True

        context = self.get_context_data(**kwargs)
        context["success"] = success
        return render(request, self.template_name, context)
