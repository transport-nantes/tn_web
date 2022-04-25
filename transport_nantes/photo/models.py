"""Models for photo competition."""

from django.db import models


class Entry(models.Model):
    """
    Represent an entry in a photo competition.

    """
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = Models.CharField(max_length=80, blank=False)
    relationship_to_competition = models.TextField(blank=True)
    photo_location = models.CharField(max_length=80, blank=True)
    photo_kit = models.TextField(blank=True)
    technical_notes = models.TextField(blank=True)
    photographer_comments = models.TextField(blank=True)
    submitted_photo = models.ImageField(
        upload_to='photo/', blank=False,
        help_text='résolution minimum : 1800 x 1800')
