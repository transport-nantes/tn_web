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

from authentication.forms import SignUpForm

def login(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            try:
                user.refresh_from_db()
                if user.profile.authenticates_by_mail:
                    send_activation(request, user)
                    return redirect('authentication:account_activation_sent', is_new=False)
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
            if len(existing_users) == 1:
                existing_user = existing_users[0]
                if existing_user.profile.authenticates_by_mail:
                    send_activation(request, existing_user)
                    return redirect('authentication:account_activation_sent', is_new=False)
            user.email = form.cleaned_data['email']
            user.username = get_random_string(20)
            user.is_active = False
            user.save()
            send_activation(request, user)
            return redirect('authentication:account_activation_sent', is_new=True)
    else:
        form = SignUpForm()
    return render(request, 'authentication/login.html', {'form': form})

def send_activation(request, user):
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
    })
    #### user.email_user(subject, message)
    print(subject)
    print(message)

def account_activation_sent(request, is_new):
    is_new_bool = (is_new == True)
    return render(request, 'authentication/account_activation_sent.html', {'is_new': is_new_bool})

def activate(request, token):
    """Process an activation token.

    The result should be (1) to flag the user as having a valid email
    address and (2) to login the user.

    """
    user_id = token_valid(token)
    if user_id < 0:
        return render(request, 'account_activation_invalid.html')
    try:
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        auth.login(request, user)
        return redirect('index')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return render(request, 'account_activation_invalid.html')

class DeauthView(LogoutView):
    """Log out the user.

    Renders the home page (but not by its view function, just via the
    template, which is odd.  If the current page doesn't require
    login, we should probably stay put, but that's neither important
    now nor do I know how to do it.

    """
    template_name = "asso_tn/index.html"
