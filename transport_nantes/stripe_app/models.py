from django.db import models
from django.contrib.auth.models import User


class TrackingProgression(models.Model):
    """
    Stores a user progress through the donation form

    amount_form_done: The user completed a valid amount form.
    donation_form_done: The user completed a valid donation form and
    redirected to Stripe.
    timestamp: The time user left the page (completed or not)
    tn_session : Random 20 long string stored in cookies to identify
    the browser.
    """
    amount_form_done = models.BooleanField(verbose_name="Formulaire montant")
    donation_form_done = models.BooleanField(
        verbose_name="Formulaire informations personnelles")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    tn_session = models.CharField(max_length=50, verbose_name="Session",
                                  null=True)
    browser = models.CharField(
        max_length=50, verbose_name="Navigateur", null=True)
    browser_version = models.CharField(
        max_length=50, verbose_name="Version du navigateur", null=True)
    os = models.CharField(max_length=50, verbose_name="OS", null=True)
    os_version = models.CharField(
        max_length=50, verbose_name="Version de l'OS", null=True)
    device_family = models.CharField(
        max_length=50, verbose_name="Famille d'appareils", null=True)
    device_brand = models.CharField(
        max_length=50, verbose_name="Marque", null=True, default="Unknown")
    device_model = models.CharField(
        max_length=50, verbose_name="Modèle", null=True, default="Unknown")
    is_mobile = models.BooleanField(verbose_name="Est un mobile", null=True)
    is_tablet = models.BooleanField(
        verbose_name="Est une tablette", null=True)
    is_touch_capable = models.BooleanField(
        verbose_name="Est tactile", null=True)
    is_pc = models.BooleanField(verbose_name="Est PC", null=True)
    is_bot = models.BooleanField(verbose_name="Est un bot", null=True)

    def __str__(self):
        if self.donation_form_done is True:
            name = "SUCCESS "
        else:
            name = "ABANDON "
        return name + str(self.timestamp)[:19]


class Donation(models.Model):
    """
    Stores information about a donation made to Mobilitains.

    Data are collected from the donation form.

    Triggered by the reception of a "checkout.session.completed" event
    from Stripe to our website's webhook.
    """

    stripe_customer_id = models.CharField(max_length=50, null=True)
    # We should *never* delete users or donation records.
    # Still, we model correctly for relational integrity.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    email = models.EmailField(verbose_name="Email")
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    address = models.CharField(max_length=200, verbose_name="Adresse")
    more_address = models.CharField(max_length=200,
                                    verbose_name="Complément d'adresse",
                                    blank=True)
    postal_code = models.CharField(max_length=10, verbose_name="Code postal")
    city = models.CharField(max_length=100, verbose_name="Ville")
    country = models.CharField(max_length=100, verbose_name="Pays")

    # A period of 0 means a one-time gift.
    # Any other value means repeat at N month intervals.
    # We should limit this to 12 max.
    periodicity_months = models.IntegerField(verbose_name="Période")
    amount_centimes_euros = models.IntegerField(
        verbose_name="Montant (Centimes €)", default=0)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    originating_view = models.CharField(max_length=100,
                                        default=None, null=True)
    originating_parameters = models.CharField(max_length=100,
                                              default=None, null=True)

    def __str__(self):
        if self.periodicity_months == 0:
            return self.first_name + " " + self.last_name + \
                " ({}) ".format(self.email) +\
                str(round(float(self.amount_centimes_euros/100), 2)) \
                + "€ ONE-TIME" + str(self.timestamp)[:19]
        else:
            return self.first_name + " " + self.last_name + \
                " ({}) ".format(self.email) +\
                str(round(float(self.amount_centimes_euros/100), 2)) \
                + "€ SUBSCRIPTION" + str(self.timestamp)[:19]
