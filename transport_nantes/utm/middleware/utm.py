from utm.models import UTM

tracked_params = [
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",

    # Advertisers.
    "aclk",
    "fbclid",
    "gclid",
    "msclkid",
    "twclid",
]

class UtmMiddleware:

    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        """Called on each request."""
        response = self.get_response(request)
        params = {k: v for k, v in request.GET.items() if k in tracked_params}
        if (len(params) > 0):
            utm = UTM()
            utm.base_url = request.path
            utm.session_id = request.COOKIES.get('sessionid', '-')

            if 'utm_campaign' in params:
                utm.campaign = params['utm_campaign']
            if 'utm_content' in params:
                utm.content = params['utm_content']
            if 'utm_medium' in params:
                utm.medium = params['utm_medium']
            if 'utm_source' in params:
                utm.source = params['utm_source']
            if 'utm_term' in params:
                utm.term = params['utm_term']

            if 'aclk' in params:
                utm.aclk = True
            if 'fbclid' in params:
                utm.fbclid = True
            if 'gclid' in params:
                utm.gclid = True
            if 'msclkid' in params:
                utm.msclkid = True
            if 'twclid' in params:
                utm.twclid = True

            utm.save()

        return response
