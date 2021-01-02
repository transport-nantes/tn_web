from django.conf import settings
from django.contrib.sites.models import Site

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

class DynamicSiteDomainMiddleware:
    default_site_id = None

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        self.default_site_id = settings.DEFAULT_SITE_ID
        if self.default_site_id is not None:
            current_site = Site.objects.get(id=self.default_site_id)

    def __call__(self, request):
        if self.default_site_id is None:
            try:
                current_site = Site.objects.get(domain=request.get_host())
            except Site.DoesNotExist:
                current_site = Site.objects.get(id=settings.DEFAULT_SITE_ID)
        else:
            current_site = Site.objects.get(id=self.default_site_id)

        request.current_site = current_site
        settings.SITE_ID = current_site.id

        response = self.get_response(request)
        return response
