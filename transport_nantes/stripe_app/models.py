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
