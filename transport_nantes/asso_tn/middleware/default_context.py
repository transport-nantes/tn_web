from copy import copy
from django.conf import settings
from django.template import RequestContext

# Middleware to set default social media data.
#
# This bit of middleware has been used and reused, notably for the
# (now no longer used) Sites module.  We may or may not still need
# this, at least in its current form.


class DefaultContextMiddleware:
    social_media_context = {
        # This assumes images are served from STATIC.
        # We'll need to change something (in base?) when using MEDIA.
        'og_image_default': 'velopolitain/v1.png',
        'og_image_alt': 'mobilité',
        'twitter_image_default': "asso_tn/mobilite-pour-tous.jpg",
        'og_twitter_title_default': ("Mobilitains - Pour une "
                                     "mobilité multimodale"),
        'og_twitter_description_default': ("Nous agissons pour une mobilité "
                                           "plus fluide, plus sécurisée "
                                           "et plus vertueuse"),
        'twitter_site': "@Mobilitains",
        'twitter_creator': "@Mobilitains",
        'twitter_card': "summary_large_image",
    }

    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        context = RequestContext(request)
        settings.csrf_token = request.COOKIES.get(
            settings.CSRF_COOKIE_NAME, "")
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        # This runs after the view.
        my_context = copy(self.social_media_context)
        if 'social' in response.context_data:
            print('--')
            for key, value in response.context_data["social"].items():
                if value:
                    my_context[key] = value
        response.context_data["social"] = my_context
        return response
