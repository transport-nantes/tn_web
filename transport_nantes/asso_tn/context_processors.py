"""
Some request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only
parameter and returns a dictionary to add to the context.

These are referenced from the 'context_processors' option of the
configuration of a DjangoTemplates backend and used by RequestContext.

"""

from django.conf import settings


def role(request):
    """
    The settings_local.py should define a role.  Make sure it's
    provided in the context, as well as a boolean for whether or not
    we're running in production.
    """
    if hasattr(settings, "ROLE"):
        role = settings.ROLE
    else:
        role = "unknown"
    if "production" == role:
        is_prod = True
    else:
        is_prod = False
    return {"role": role, "is_production": is_prod}
