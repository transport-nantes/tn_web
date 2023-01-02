from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone

# Create your models here.


class ClickableCollectable(models.Model):
    """Represent things that can be clicked and collected."""

    collectable = models.CharField(max_length=80, blank=False)
    collectable_token = models.CharField(
        max_length=80, blank=False, unique=True
    )


class ClickAndCollect(models.Model):
    """Represent a click-and-collect instances.

    We want to represent people (who are de facto users in order to
    store their user data) as well as the details of what they are
    clicking or collecting.

    In the first instance of this model, we only use it for the
    lockdown reflective vest campaign.

    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collectable = models.ForeignKey(
        ClickableCollectable, on_delete=models.CASCADE
    )
    reserve_datetime = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return "{c} . .  {fn} {ln} <{email}>  ({dt})".format(
            c=self.collectable.collectable,
            fn=self.user.first_name,
            ln=self.user.last_name,
            email=self.user.email,
            dt=self.reserve_datetime,
        )
