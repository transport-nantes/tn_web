import logging

from django.views.generic.edit import FormView
from django.core.mail import send_mail
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.urls import reverse
from django.views.generic.base import TemplateView

from authentication.forms import (EmailLoginForm, PasswordLoginForm,
                                  UserUpdateForm, ProfileUpdateForm)
from asso_tn.utils import make_timed_token, token_valid


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
            # Don't create new users until then confirm (respond to mail).
            authenticates_by_email = True
        if authenticates_by_email:
            logger.info(f"Sending email to {email}")
            send_activation(self.request, email, remember_me)
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
    subject = 'sujet'
    message = render_to_string(
        'authentication/account_activation_email.html',
        {  # request.build_absolute_uri(),
            'scheme': request.scheme,
            'host': request.get_host(),
            'token': make_timed_token(email, 20),
            'remember_me': remember_me,
        })

    if hasattr(settings, 'ROLE') and settings.ROLE in ['beta', 'production']:
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False)
        except Exception as e:
            logger.error(f"Error while sending mail to {email} : {e}")

    else:
        print(f"Sent message : \n{message}")


class ActivationLoginView(TemplateView):

    template_name = "authentication/mail_confirmed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get('token', '')
        email, remember_me = token_valid(token)
        if email is None:
            self.template_name = \
                'authentication/account_activation_invalid.html'
            return context

        try:
            user = User.objects.get(email=email)
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

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            self.template_name = \
                'authentication/account_activation_invalid.html'

        return context


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
