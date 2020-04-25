from datetime import date

from django.conf import settings
from django.utils.crypto import salted_hmac
from django.utils.crypto import secrets
from django.utils.http import base36_to_int, int_to_base36

def make_timed_token(minutes):
    """Make a URL-safe timed token that's valid for minutes minutes.
    """
    secret = settings.SECRET_KEY
    rand_value = secrets.token_urlsafe(20)
    now = datetime.datetime.now().timestamp()
    soon = int_to_base36(int(now + 60 * minutes))
    hmac = salted_hmac(soon, rand_value).hexdigest()[:20]
    return '{rnd}|{t}|{h}'.format(
        rnd=rand_value,
        t=soon,
        h=hmac)

def minutes_remaining(timed_token):
    """Validate a timed token.

    Return true if it is valid, false if it is not (either because
    it is malformed or because it has expired.
    """
    the_rand_value, the_soon, the_hmac = timed_token.split('|')
    computed_hmac = salted_hmac(the_soon, the_rand_value).hexdigest()[:20]
    if computed_hmac != the_hmac:
        return False
    now = datetime.datetime.now().timestamp()
    if now > base36_to_int(the_soon):
        return False
    return True
