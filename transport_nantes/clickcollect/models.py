from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone
import uuid

# Create your models here.

class ClickableCollectable(models.Model):
    """Represent things that can be clicked and collected.
    """
    collectable = models.CharField(max_length=80, blank=False)
    collectable_token = models.CharField(max_length=80, blank=False,
                                         unique=True)

class ClickAndCollect(models.Model):
    """Represent a click-and-collect instances.

    We want to represent people (who are de facto users in order to
    store their user data) as well as the details of what they are
    clicking or collecting.

    In the first instance of this model, we only use it for the
    lockdown reflective vest campaign.

    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    collectable = models.ForeignKey(ClickableCollectable,
                                    on_delete=models.CASCADE)
    reserve_datetime = models.DateTimeField(default=django.utils.timezone.now)
