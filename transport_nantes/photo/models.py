"""Models for photo competition."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


def validate_submitted_photo(value):
    """Validates that the photo meets the minimum requirements"""
    longest_side = max(value.width, value.height)
    if longest_side < 1000:
        raise ValidationError(
            'La plus grande dimension de la photo doit être supérieure '
            'à 1000px.')


class PhotoEntry(models.Model):
    """
    Represent an entry in a photo competition.

    """
    class Meta:
        verbose_name = "Photo Entry"
        verbose_name_plural = "Photo Entries"

    class CategoryType(models.TextChoices):
        PIETON_URBAIN = 'PIETON_URBAIN', 'Piéton urbain'
        LA_VIE_EN_FAMILLE = 'LA_VIE_EN_FAMILLE', 'La vie en famille'
        L_AMOUR = 'L_AMOUR', "L'amour"
        LE_TRAVAIL = 'LE_TRAVAIL', 'Le travail'
        LE_PHOTOJOURNALISME = 'LE_PHOTOJOURNALISME', 'Le photojournalisme'
        PHOTOGRAPHE_SENIOR = 'PHOTOGRAPHE_SENIOR', 'Photographe senior'
        JEUNE_PHOTOGRAPHE = 'JEUNE_PHOTOGRAPHE', 'Jeune photographe'

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.CharField(
        max_length=80,
        choices=CategoryType.choices,
        verbose_name="Catégorie")
    relationship_to_competition = models.TextField(
        blank=True,
        verbose_name=("Comment cette photo est-elle en relation avec le "
                      "quartier des Hauts-Pavés ?"))
    photo_location = models.TextField(
        blank=True,
        verbose_name="Lieu de la photo")
    photo_kit = models.TextField(blank=True, verbose_name="Appareil photo")
    technical_notes = models.TextField(
        blank=True,
        verbose_name="Notes techniques")
    photographer_comments = models.TextField(
        blank=True,
        verbose_name="Commentaires du photographe")
    submitted_photo = models.ImageField(
        upload_to='photo/', blank=False,
        help_text="Largeur de la photo recommandée : 2000 px",
        verbose_name="Photo",
        validators=[validate_submitted_photo])

    def __str__(self):
        return f"{self.user.username} - {self.category}"
