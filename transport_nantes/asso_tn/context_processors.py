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
    if hasattr(settings, 'ROLE'):
        role = settings.ROLE
    else:
        role = 'unknown'
    if 'production' == role:
        is_prod = True
    else:
        is_prod = False
    return {'role': role, 'is_production': is_prod}

## Default context for the base template.
social_media_context = {
    # This assumes images are served from STATIC.
    # We'll need to change something (in base?) when using MEDIA.
    'og_image': 'velopolitain/v1.png',
    'og_image_alt': '',
    ## Optional but would be nice some day.
    ##
    ## Providing defaults may or may not be reasonable, since it would
    ## require us to provide the values at all times with every og
    ## image.
    ##
    #'og_image_type':,
    #'og_image_width':,
    #'og_image_height':,
    'twitter_image': "asso_tn/mobilite-pour-tous.jpg",
    'twitter_title': "Mobilitains - Pour une mobilité multimodale",
    'twitter_description': "Nous agissons pour une mobilité plus fluide, plus sécurisée et plus vertueuse",
    'twitter_site': "@Mobilitains",
    'twitter_creator': "@Mobilitains",
    'twitter_card': "summary_large_image",
}

def default_context(request):
    """
    """
    return {'social': social_media_context }
