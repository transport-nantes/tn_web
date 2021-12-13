from django.db import models

class UTM(models.Model):
    """Model used to track where our traffic comes from.

    We also track arriving advertising tokens, although we can't do
    anything with them besides note that, by their presence, they
    indicate users arriving via one of those sources.

    While we maintain a schema of what UTM values we wish to use, here
    we are agnostic.  If someone shares links to us with other values,
    we still want to note it (in the event that they are successful,
    especially).

    We explicitly do not store user, ip address, or other PII here.

    At some point it may be useful to add rough geographic data for
    better understanding urban/rural divisions.

    """
    # The URL without ? arguments.
    base_url = models.CharField(max_length=200, blank=False)
    # A cookie that is unique to visitors for a while so that we can
    # stitch together multiple visits.
    session_id = models.CharField(max_length=200, blank=False)

    # Cf. https://en.wikipedia.org/wiki/UTM_parameters
    campaign = models.CharField(max_length=100, blank=True)
    content = models.CharField(max_length=100, blank=True)
    medium = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=100, blank=True)
    term = models.CharField(max_length=100, blank=True)

    # Bing / Microsoft
    aclk = models.BooleanField(blank=True, default=False)
    # Facebook
    fbclid = models.BooleanField(blank=True, default=False)
    # Google
    gclid = models.BooleanField(blank=True, default=False)
    # Microsoft Network
    msclkid = models.BooleanField(blank=True, default=False)
    # Twitter
    twclid = models.BooleanField(blank=True, default=False)

    timestamp = models.DateTimeField(auto_now=True)
