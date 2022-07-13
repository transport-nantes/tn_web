import logging

from django.db import models
from django.forms import ValidationError

logger = logging.getLogger("django")


class Session(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    address = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=5, blank=True, null=True)
    total_number_of_pedestrians = models.IntegerField(default=0)
    total_number_of_bicycles = models.IntegerField(default=0)
    total_number_of_motor_vehicles = models.IntegerField(default=0)
    total_number_of_public_transports = models.IntegerField(default=0)
    user_agent_browser = models.CharField(max_length=255, blank=True, null=True)
    start_timestamp = models.DateTimeField()
    end_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.email} - {self.start_timestamp}'

    def create_event(self, event_type):
        Event.objects.create(
            session=self,
            type=event_type,
        )
        logger.info(f"{self.user.email} created an event of type {event_type}")


def event_type_validator(value):
    """Validate that the recorded event type is a valid event type."""
    if value not in Event.EventTypes.values:
        raise ValidationError(
            f'{value} is not a valid event type.'
            f'Valid event types are : {Event.EventTypes.choices}')


class Event(models.Model):

    class EventTypes(models.TextChoices):
        PEDESTRIAN = 'PEDESTRIAN', 'pedestrian'
        BICYCLE = 'BICYCLE', 'bicycle'
        MOTOR_VEHICLE = 'MOTOR-VEHICLE', 'motor vehicle'
        PUBLIC_TRANSPORT = 'PUBLIC-TRANSPORT', 'public-transport'

    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(
        max_length=255, choices=EventTypes.choices, validators=[event_type_validator])

    def __str__(self):
        return f'{self.session.user.email} - {self.timestamp} - {self.type}'

    def save(self, *args, **kwargs) -> None:
        """Override save method to run validators on create"""
        try:
            self.full_clean()
            super().save(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Error while saving event : {e}")
