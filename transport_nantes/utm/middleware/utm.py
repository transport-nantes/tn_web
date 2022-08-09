import user_agents

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
        # Code to be executed for each request before the view (and
        # later middleware) are called.
        if not request.path.startswith('/admin/') and \
           not request.path.startswith('/favicon.ico'):
            utm = UTM()
            utm.base_url = request.path
            utm.session_id = request.session.get('tn_session', '-')

            # If for some reason we receive no user agent data, the
            # device, os, and browser will be set to "Other" and the
            # booleans will all be false.
            user_agent = user_agents.parse(request.META.get('HTTP_USER_AGENT', ''))
            utm.ua_device = user_agent.get_device()
            utm.ua_os = user_agent.get_os()
            utm.ua_browser = user_agent.get_browser()
            utm.ua_is_table = user_agent.is_tablet
            utm.ua_is_mobile = user_agent.is_mobile
            utm.ua_is_touch_capable = user_agent.is_touch_capable
            utm.ua_is_pc = user_agent.is_pc
            utm.ua_is_bot = user_agent.is_bot
            utm.ua_is_email_client = user_agent.is_email_client

            params = {k: v for k, v in request.GET.items() if k in tracked_params}

            utm.campaign = params.get('utm_campaign', '')
            utm.content = params.get('utm_content', '')
            utm.medium = params.get('utm_medium', '')
            utm.source = params.get('utm_source', '')
            utm.term = params.get('utm_term', '')

            utm.aclk = ('aclk' in params)
            utm.fbclid = ('fbclid' in params)
            utm.gclid = ('gclid' in params)
            utm.msclkid = ('msclkid' in params)
            utm.twclid = ('twclid' in params)

            utm.user_is_authenticated = request.user.is_authenticated

            utm.save()

        response = self.get_response(request)

        # Code to be executed for each request/response after the view
        # is called.
        return response
