from django.contrib.auth.models import User

import logging

from django.db import models
from django.forms import ValidationError

logger = logging.getLogger("django")


class MobilitoUser(models.Model):
    """Maintain information about Mobilito users."""

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+')
    # Set first_time to False once the user has read the tutorial.
    first_time = models.BooleanField(default=True)


class Session(models.Model):
    """A user recording session: a collection of Event's."""
    user = models.ForeignKey(MobilitoUser, on_delete=models.PROTECT)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(null=True, blank=True)
    pedestrian_count = models.IntegerField(null=True)
    bicycle_count = models.IntegerField(null=True)
    motor_vehicle_count = models.IntegerField(null=True)
    public_transport_count = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.user.email} - {self.start_timestamp}'

    def create_event(self, event_type):
        Event.objects.create(
            session=self,
            event_type=event_type,
        )
        logger.info(f"{self.user.email} created an event of type {event_type}")


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

    session = models.ForeignKey(Session, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(
        max_length=50,          # Arbitrary, too much is enough.
        choices=EventTypes.choices,
        validators=[event_type_validator],
        blank=False)

    def __str__(self):
        return f'{self.session.user.user.email} - {self.timestamp} - {self.event_type.label}'
