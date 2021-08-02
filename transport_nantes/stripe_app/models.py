from django.db import models


class TrackingProgression(models.Model):
    amount_form_done = models.BooleanField(verbose_name="Formulaire montant")
    donation_form_done = models.BooleanField(
        verbose_name="Formulaire informations personnelles")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    def __str__(self):
        if self.donation_form_done is True:
            name = "SUCCESS "
        else:
            name = "ABANDON "
        return name + str(self.timestamp)[:19]


class Donor(models.Model):
    email = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    telephone = models.CharField(max_length=13)
    title = models.CharField(choices=[
                                ("M", "Monsieur"),
                                ("MME", "Madame"),
                                ("MMM", "Autre")],
                             max_length=3,
                             verbose_name="Title")
    address = models.CharField(max_length=150)
    more_adress = models.CharField(blank=True, max_length=150)
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=150)
    country = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    mode = models.CharField(
        choices=[("SUB", "Subscription"), ("PAY", "One time donation")],
        max_length=50)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.donor) + " | " + str(self.amount) + " | " +\
            str(self.mode) + " | " + str(self.timestamp)[:19]
