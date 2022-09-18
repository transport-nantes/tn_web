import user_agents

from gom_jabbar.models import Visit

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


class GomJabbarMiddleware:

    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        """Called on each request."""
        # Code to be executed for each request before the view (and
        # later middleware) are called.
        if not request.path.startswith('/admin/') and \
           not request.path.startswith('/favicon.ico'):
            visit = Visit()
            visit.base_url = request.path
            visit.session_id = request.session.get('tn_session', '-')

            # If for some reason we receive no user agent data, the
            # device, os, and browser will be set to "Other" and the
            # booleans will all be false.
            user_agent = user_agents.parse(request.META.get('HTTP_USER_AGENT', ''))
            visit.ua_device = user_agent.get_device()
            visit.ua_os = user_agent.get_os()
            visit.ua_browser = user_agent.get_browser()
            visit.ua_is_table = user_agent.is_tablet
            visit.ua_is_mobile = user_agent.is_mobile
            visit.ua_is_touch_capable = user_agent.is_touch_capable
            visit.ua_is_pc = user_agent.is_pc
            visit.ua_is_bot = user_agent.is_bot
            visit.ua_is_email_client = user_agent.is_email_client

            params = {k: v for k, v in request.GET.items() if k in tracked_params}

            visit.campaign = params.get('utm_campaign', '')
            visit.content = params.get('utm_content', '')
            visit.medium = params.get('utm_medium', '')
            visit.source = params.get('utm_source', '')
            visit.term = params.get('utm_term', '')

            visit.aclk = ('aclk' in params)
            visit.fbclid = ('fbclid' in params)
            visit.gclid = ('gclid' in params)
            visit.msclkid = ('msclkid' in params)
            visit.twclid = ('twclid' in params)

            visit.user_is_authenticated = request.user.is_authenticated

            visit.save()

        response = self.get_response(request)

        # Code to be executed for each request/response after the view
        # is called.
        return response
