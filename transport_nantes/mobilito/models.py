from django.contrib.auth.models import User

import logging

from django.db import models, IntegrityError
from django.forms import ValidationError

logger = logging.getLogger("django")


class MobilitoUser(models.Model):
    """Maintain information about Mobilito users."""

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    # Set first_time to False once the user has read the tutorial.
    first_time = models.BooleanField(default=True)
    # Set to the date user visited every page of the tutorial for the last
    # time.
    completed_tutorial_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.email


class MobilitoSession(models.Model):

    class Meta:
        permissions = (
            ("mobilito_session.view_session", "Can view an unpublished session"),
        )

    """A user recording session: a collection of Event's."""
    user = models.ForeignKey(MobilitoUser, on_delete=models.PROTECT)
    location = models.CharField(max_length=1000, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    user_browser = models.CharField(max_length=255, blank=True, null=True)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(null=True, blank=True)
    pedestrian_count = models.IntegerField(default=0)
    bicycle_count = models.IntegerField(default=0)
    motor_vehicle_count = models.IntegerField(default=0)
    public_transport_count = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    session_sha1 = models.CharField(max_length=200, unique=True, editable=False)

    def __str__(self):
        return f'{self.user.user.email} - {self.start_timestamp}'

    def create_event(self, event_type):
        Event.objects.create(
            mobilito_session=self,
            event_type=event_type,
        )
        logger.info(f"{self.user.user.email} created an event of type {event_type}")

    def save(self, *args, **kwargs):
        if not self.session_sha1:
            self.session_sha1 = self.generate_session_sha1()

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            logger.warning(f"Session {self.session_sha1} already exists")
            self.session_sha1 = self.generate_session_sha1()
            logger.warning(f"New session SHA1: {self.session_sha1}")
            super().save(*args, **kwargs)

    def generate_session_sha1(self):
        """Compute a sha1 from now() and the users's ID"""
        import hashlib
        import time
        return hashlib.sha1(
            (
                str(time.monotonic_ns()) + "|" + str(self.user.user.id)
            ).encode('utf-8')
        ).hexdigest()


def event_type_validator(value):
    """Validate that the recorded event type is a valid event type."""
    if value not in Event.EventTypes.values:
        raise ValidationError(
            f'{value} is not a valid event type.'
            f'Valid event types are : {Event.EventTypes.choices}')


class Event(models.Model):
    """Model one press of a count button."""
    class EventTypes(models.TextChoices):
        PEDESTRIAN = 'ped'
        BICYCLE = 'bike'
        MOTOR_VEHICLE = 'car'
        PUBLIC_TRANSPORT = 'TC'

    mobilito_session = models.ForeignKey(MobilitoSession, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=50,          # Arbitrary, too much is enough.
        choices=EventTypes.choices,
        validators=[event_type_validator],
        blank=False)

    def __str__(self):
        return f'{self.mobilito_session.user.user.email} - {self.timestamp} - {self.event_type}'

    def save(self, *args, **kwargs) -> None:
        """Override save method to run validators on create"""
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error while saving event : {e}")
