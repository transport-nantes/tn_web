from django.db import models
from django.contrib.auth.models import User


class TrackingProgression(models.Model):
    """
    Stores a user progress through the donation form

    amount_form_done: The user completed a valid amount form.
    donation_form_done: The user completed a valid donation form and
    redirected to Stripe.
    timestamp: The time user left the page (completed or not)
    """
    amount_form_done = models.BooleanField(verbose_name="Formulaire montant")
    donation_form_done = models.BooleanField(
        verbose_name="Formulaire informations personnelles")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")
    user_agent = models.CharField(
        max_length=255, verbose_name="User agent", null=True)

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

    def __str__(self):
        return self.first_name + " " + self.last_name + \
            " ({}) ".format(self.email) +\
            str(round(float(self.amount_centimes_euros/100), 2)) \
            + "€ " + str(self.timestamp)[:19]
