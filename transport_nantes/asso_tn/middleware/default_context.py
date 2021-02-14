from copy import copy
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import RequestContext

# Middleware to dynamically set the current site.
#
# The plan is that we no longer need to set SITE_ID and only
# developers should have to set DEFAULT_SITE_ID in their settings_?.py
# file (the thing that sets WSGI_APPLICATION).  At issue is that
# setting SITE_ID by index number is fragile.  Just adding and
# removing records from the database change the index number.
#
# It's possible to set SITE_ID =
# Site.objects.get(name='my_site_name').id, but this doesn't work in
# settings, where database connectivity and credentials are not yet
# reliably set.  And later on, in the running (non-startup) code, we
# don't know what the site name is supposed to be.
#
# So this bit of code looks at the host in the request and looks that
# up in the sites table.  If it finds it, it uses it.  Otherwise, it
# sets the value to DEFAULT_SITE_ID (which is what developers should
# set).
#
# Based on https://stackoverflow.com/a/64037438/833300 .

class DefaultContextMiddleware:
    social_media_context = {
        # This assumes images are served from STATIC.
        # We'll need to change something (in base?) when using MEDIA.
        'og_image': 'velopolitain/v1.png',
        'og_image_alt': 'mobilité',
        'twitter_image': "asso_tn/mobilite-pour-tous.jpg",
        'twitter_title': "Mobilitains - Pour une mobilité multimodale",
        'twitter_description': "Nous agissons pour une mobilité plus fluide, plus sécurisée et plus vertueuse",
        'twitter_site': "@Mobilitains",
        'twitter_creator': "@Mobilitains",
        'twitter_card': "summary_large_image",
    }

    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # This runs after the view.
        my_context = copy(self.social_media_context)
        my_context.update(response.context_data["social"])
        response.context_data["social"] = my_context
        return response
