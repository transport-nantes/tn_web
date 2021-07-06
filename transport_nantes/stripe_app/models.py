from django.db import models

# Create your models here.
class TrackingProgression(models.Model):
    step_1 = models.BooleanField()
    step_2 = models.BooleanField()
    timestamp =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.step_2 is True:
            name  = "SUCCESS "
        else:
            name = "ABANDON "
        return name +  str(self.timestamp)[:19]

class Donator(models.Model):
    email = models.EmailField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    telephone = models.CharField(max_length=13)
    gender = models.CharField(choices=[
                                ("M", "Monsieur"),
                                ("MME", "Madame")], max_length=3)
    address = models.CharField(max_length=50)
    more_adress = models.CharField(blank=True, max_length=50)
    postal_code = models.IntegerField()
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

class Donation(models.Model):
    donator = models.ForeignKey(Donator, on_delete=models.CASCADE)
    mode = models.CharField(
        choices=[("SUB", "Subscription"), ("PAY", "One time donation")], max_length=50)
    amount = models.FloatField()
