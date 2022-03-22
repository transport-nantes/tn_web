import datetime
from functools import wraps
import logging

from django.conf import settings
from django.http.response import HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.crypto import salted_hmac
from django.utils.crypto import secrets
from django.utils.http import base36_to_int, int_to_base36
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from hashlib import sha1, sha256


logger = logging.getLogger("django")


# Don't reveal our secret key, but we'd like something that is
# nonetheless our secret so that we can validate timed tokens we
# created.  SHA1 is broken (with great effort), but we'll wrap it in
# SHA256 below.
hashed_secret = sha1(settings.SECRET_KEY.encode()).hexdigest()


def make_timed_token(string_key, minutes, int_key=0, test_value_now=None):
    """Make a URL-safe timed token that's valid for minutes minutes.

    This was originally meant for use with confirmation mails to avoid
    having to hold state on the server: the string_key is the user's
    email address, the int_key is 0 or 1, according to whether the
    user checked "remember me".

    In this case (auth), the token is tied to a specific user
    (identified by email address, the string_key) to avoid frauds
    where a token is used to validate a different user than the one
    intended (i.e., to validate a user whose email the person doesn't
    control or by simple fishing for email).  We insert a random
    number (and our own secret key) to avoid replay attacks.

    The integer int_key was originally conceived for setting session
    cookies, but these functions make no assumption other than that it
    is an integer.  The auth functions should assume that 0 means
    unchecked "remember me" and 1 means "remember me" and anything
    else is invalid.

    Note that we use this function and its paired validate function
    for other tasks as well, notably for mailing list unsubscribe
    links.

    The test_value_now is for testing and should not normally be set.

    Note that we, and therefore anyone, can reverse the token.  The
    data inserted is not secure or hidden.  Our use of our hashed
    secret key provides some guarantee that we created the token
    ourselves, but cryptography is hard, oiur crypto is not peer
    reviewed, and we simply don't expect a sufficiently powerful
    adversary to worry further.  A private relationship between
    string_key and int_key provides added comfort that the client
    should check.

    """
    rand_value = secrets.token_urlsafe(20)
    hash_rand = sha256((rand_value + hashed_secret).encode()).hexdigest()
    if test_value_now is not None:
        now = test_value_now
    else:
        now = datetime.datetime.now().timestamp()
    soon_seconds = int_to_base36(int(now + 60 * minutes))
    int_key_str = int_to_base36(int(int_key))
    hmac = salted_hmac(soon_seconds + int_key_str, rand_value + str(string_key)
                       ).hexdigest()[:20]
    token = '{rnd}|{hr}|{e}|{t}|{p}|{h}'.format(
        rnd=rand_value,
        hr=hash_rand,
        e=string_key,
        t=soon_seconds,
        p=int_key_str,
        h=hmac)
    encoded_token = urlsafe_base64_encode(token.encode())
    return encoded_token


def token_valid(encoded_timed_token, test_value_now=None):
    """Validate a timed token.

    Return the string_key for which the token is valid, if the token
    is valid.  Return None if the token is not (either because it is
    malformed or because it has expired).

    If the token is valid, also return the int_key integer.  If the
    token is not valid, int_key will be zero.

    The test_value_now is for testing and should not normally be set.

    """
    try:
        timed_token = urlsafe_base64_decode(encoded_timed_token).decode()
    except (TypeError, ValueError):
        logger.info(f"token_valid: invalid token ({encoded_timed_token})")
        return (None, 0)
    (the_rand_value, the_hash_rand, the_string_key,
     the_soon, the_int_key, the_hmac) = \
        timed_token.split('|')
    hash_rand = sha256((the_rand_value + hashed_secret).encode()).hexdigest()
    if hash_rand != the_hash_rand:
        return (None, 0)
    computed_hmac = salted_hmac(the_soon + the_int_key,
                                the_rand_value + str(the_string_key)).hexdigest()[:20]
    if computed_hmac != the_hmac:
        return (None, 0,)
    if test_value_now is not None:
        now = test_value_now
    else:
        now = datetime.datetime.now().timestamp()
    if now > base36_to_int(the_soon):
        return (None, 0)
    return (the_string_key, base36_to_int(the_int_key),)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require staff status for all views."""

    def test_func(self):
        return self.request.user.is_staff


def StaffRequired(func):
    """Decorator that checks for Staff status to access the function"""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("""Vous n'avez pas l'autorisation
            d'accéder à cette page.""")
    return wrapper


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Require Superuser status for all views."""

    login_url = reverse_lazy('authentication:login')

    def test_func(self):
        return self.request.user.is_superuser
