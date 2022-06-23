from django.contrib.auth.models import User
from django.db import models


class MobilitoUser(models.Model):
    """Maintain information about Mobilito users."""

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    # Set first_time to False once the user has read the tutorial.
    first_time = models.BooleanField(default=True)
