from asso_tn.utils import make_timed_token, token_valid

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings

from authentication.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm

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
def login(request, base_template=None):
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            remember_me = form.cleaned_data["remember_me"]
            try:
                user.refresh_from_db()
                if user.profile.authenticates_by_mail:
                    send_activation(request, user, False, remember_me)
                    return render(request, 'authentication/account_activation_sent.html', {'is_new': False})
            except ObjectDoesNotExist:
                print('ObjectDoesNotExist')
                pass            # I'm not sure this can ever happen.

            # There should be precisely one or zero existing user with the
            # given email, but since the django user model doesn't impose
            # a unique constraint on user emails, I'm stuck verifying this.
            existing_users = User.objects.filter(email=form.cleaned_data['email'])
            if len(existing_users) > 1:
                return HttpResponseServerError(
                    "Data error: Multiple email addresses found")
            
            # If password given by user connect with it else connect by mail
            password1 = form.cleaned_data["password1"]
            password2 = form.cleaned_data["password2"]
            if password1:
                # If user exists and gives password, connect him
                if len(existing_users) == 1:
                    existing_user = existing_users[0].username
                    user = auth.authenticate(username= existing_user, password= password1)

                    if user:
                        auth.login(request, user)
                        # Set session cookie expiration to session duration if "False" otherwise for 30 days
                        if remember_me == False:
                            request.session.set_expiry(0)
                        else:
                            request.session.set_expiry(60*60*24*30)
                        return redirect("index")
                # If user doesn't exist and give password, create account and send a confirmation mail
                if len(existing_users) == 0:
                    if password2 and password1 == password2:
                        user.email = form.cleaned_data['email']
                        user.username = get_random_string(20)
                        user.is_active = False
                        user.set_password(password1)
                        user.save()
                        send_activation(request, user, True, remember_me)
                        return render(request, 'authentication/account_activation_sent.html', {'is_new': True})
                    elif not password2 or password1 != password2:
                        # return to login page with password error message
                        context = {}
                        context["form"] = form
                        context["pwd_error"] = "Veuillez entrer à nouveau le mot de passe."
                        return render(request, 'authentication/login.html', context)
            
            # If no password given
            else:
                # If user exisis, send authentication mail
                if len(existing_users) == 1:
                    existing_user = existing_users[0]
                    if existing_user.profile.authenticates_by_mail:
                        send_activation(request, existing_user, False, remember_me)
                        return render(request, 'authentication/account_activation_sent.html', {'is_new': False})
                # If user doesn't exist, create account and send confirmation mail
                if len(existing_users) == 0:
                    user.email = form.cleaned_data['email']
                    user.username = get_random_string(20)
                    user.is_active = False
                    user.save()
                    send_activation(request, user, True, remember_me)
                    return render(request, 'authentication/account_activation_sent.html', {'is_new': True})
        else:
            # # Form is not valid.
            context = {}
            context["form"] = form
            return render(request, 'authentication/login.html', context)
    else:
        form = SignUpForm()
    return render(request, 'authentication/login.html', {'form': form})

def send_activation(request, user, is_new, remember_me):
    """Send user an activation/login link.

    The caller should then redirect to / render a template letting the
    user know the mail is on its way, since the redirect is a GET.

    """
    current_site = get_current_site(request)
    subject = 'Votre compte à {dom}'.format(dom=current_site.domain)
    message = render_to_string('authentication/account_activation_email.html', {
        'user_id': user.pk,
        'domain': current_site.domain,
        'token': make_timed_token(user.pk, 20),
        'is_new': is_new,
        'remember_me': remember_me,
    })
    if hasattr(settings, 'ROLE') and settings.ROLE in ['staging', 'production']:
        user.email_user(subject, message)
    elif hasattr(settings, 'ROLE') and settings.ROLE == 'test':
        print("  [Envoi de mél supprimé ici.]")
    else:
        # We're in dev.
        print("Mode dev : mél qui aurait été envoyé :")
        print(message)

def activate(request, token, remember_me, base_template=None):
    """Process an activation token.

    The result should be (1) to flag the user as having a valid email
    address and (2) to login the user.

    """
    user_id = token_valid(token)
    if user_id < 0:
        return render(request, 'authentication/account_activation_invalid.html')
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        auth.login(request, user)
        # Set session cookie expiration to session duration if "False" otherwise for 30 days
        if remember_me == "False":
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(60*60*24*30)
        return redirect('index')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'authentication/account_activation_invalid.html')

class DeauthView(LogoutView):
    """Log out the user.

    Renders the home page (but not by its view function, just via the
    template, which is odd.  If the current page doesn't require
    login, we should probably stay put, but that's neither important
    now nor do I know how to do it.

    """
    template_name = "asso_tn/index.html"

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            # messages.success(request, f'Your Profile has been Updated Successfully')
            return redirect('authentication:mod')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
    return render(request, 'authentication/profile.html', context)
