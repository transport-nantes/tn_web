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

from authentication.forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            print('1 ========================================')
            try:
                user.refresh_from_db()
            except ObjectDoesNotExist:
                print("doesn't exist")
            print('2 ========================================')

            # There should be precisely one or zero existing user with the
            # given email, but since the django user model doesn't impose
            # a unique constraint on user emails, I'm stuck verifying this.
            existing_users = User.objects.filter(email=form.cleaned_data['email'])
            if len(existing_users) > 1:
                return HttpResponseServerError(
                    "Data error: Multiple email addresses found")
            print('3 ========================================')
            user.email = form.cleaned_data['email']
            user.username = get_random_string(20)
            user.is_active = False
            user.save()
            print('4 ========================================')

            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('authentication/account_activation_email.html', {
                'user_id': user.pk,
                'domain': current_site.domain,
                'token': make_timed_token(user.pk, 20),
            })
            #### user.email_user(subject, message)
            print(subject)
            print(message)
            return redirect(reverse('authentication:account_activation_sent'))
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'authentication/account_activation_sent.html')

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


