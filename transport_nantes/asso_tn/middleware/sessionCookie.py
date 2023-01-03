from django.utils.crypto import get_random_string


class SessionCookieMiddleWare:
    """
    Adds the session cookie in each request.
    """

    def __init__(self, get_response):
        """One-time configuration and initialization."""
        self.get_response = get_response

    def __call__(self, request):
        # Add a session cookie to requests if absent.
        request = self.process_request(request)
        response = self.get_response(request)

        # Communicate the session cookie to the client if absent.
        response = self.process_response(request, response)
        return response

    def process_request(self, request):
        """
        Adds the session cookie in each request.
        """
        request.session.clear_expired()
        if not request.session.get("tn_session"):
            request.session["tn_session"] = get_random_string(20)
            k_six_months_in_seconds = 15552000
            request.session.set_expiry(k_six_months_in_seconds)
        return request

    def process_response(self, request, response):
        """
        Adds the session cookie in each response.
        """
        if not request.session.get("tn_session"):
            response.set_cookie("tn_session", request.session)
        return response
