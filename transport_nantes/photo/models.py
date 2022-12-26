"""Models for photo competition."""
import logging
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models


logger = logging.getLogger("django")


def validate_submitted_photo(value):
    """Validates that the photo meets the minimum requirements"""
    longest_side = max(value.width, value.height)
    if longest_side < 1000:
        raise ValidationError(
            "La plus grande dimension de la photo doit être supérieure " "à 1000px."
        )


class PhotoEntry(models.Model):
    """
    Represent an entry in a photo competition.

    """

    class Meta:
        verbose_name = "Photo Entry"
        verbose_name_plural = "Photo Entries"
        permissions = (
            ("may_accept_photo", "May accept photos"),
            ("may_see_unaccepted_photos", "May see unaccepted photos"),
        )

    class CategoryType(models.TextChoices):
        PIETON_URBAIN = "PIETON_URBAIN", "Piéton urbain"
        LA_VIE_EN_FAMILLE = "LA_VIE_EN_FAMILLE", "La vie en famille"
        L_AMOUR = "L_AMOUR", "L'amour"
        LE_TRAVAIL = "LE_TRAVAIL", "Le travail"
        LE_PHOTOJOURNALISME = "LE_PHOTOJOURNALISME", "Le photojournalisme"
        PHOTOGRAPHE_SENIOR = "PHOTOGRAPHE_SENIOR", "Photographe senior"
        JEUNE_PHOTOGRAPHE = "JEUNE_PHOTOGRAPHE", "Jeune photographe"

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.CharField(
        max_length=80, choices=CategoryType.choices, verbose_name="Catégorie"
    )
    relationship_to_competition = models.TextField(
        blank=True,
        verbose_name=(
            "Comment cette photo est-elle en relation avec le "
            "quartier des Hauts-Pavés ?"
        ),
    )
    photo_location = models.TextField(blank=True, verbose_name="Lieu de la photo")
    photo_kit = models.TextField(blank=True, verbose_name="Appareil photo")
    technical_notes = models.TextField(blank=True, verbose_name="Notes techniques")
    photographer_comments = models.TextField(
        blank=True, verbose_name="Vos commentaires sur la photo"
    )
    submitted_photo = models.ImageField(
        upload_to="photo/",
        blank=False,
        help_text="Largeur de la photo recommandée : 2000 px",
        verbose_name="Photo",
        validators=[validate_submitted_photo],
    )
    timestamp = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Date de soumission",
        auto_now_add=True,
    )
    # Photo entries are pending (null) until they are accepted (True)
    # or rejected (False) after a jury session.
    accepted = models.BooleanField(null=True, blank=True, default=None)

    # A publicly displayable identifier for the photographer.
    photographer_identifier = models.TextField(blank=True, null=True)
    # Markdown text field where we'll add some interesting information
    # about pedestrian issues.
    pedestrian_issues_md = models.TextField(
        blank=True, null=True, verbose_name="Remarques piétons (markdown)"
    )
    # Markdown text field where we'll add information about the submitter
    # and how the photo was taken.
    submitter_info_md = models.TextField(
        blank=True, null=True, verbose_name="Remarques photo (markdown)"
    )

    # sha1 is used to generate a unique URL for each photo entry while keeping
    # the ID private.
    sha1_name = models.CharField(max_length=200, unique=True, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.category}"

    def save(self, *args, **kwargs):
        if not self.sha1_name:
            self.sha1_name = self.generate_entry_sha1()

        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            logger.warning(f"PhotoEntry {self.sha1_name} already exists")
            self.sha1_name = self.generate_entry_sha1()
            logger.warning(f"New session SHA1: {self.sha1_name}")
            self.save(*args, **kwargs)

    def generate_entry_sha1(self):
        """Compute a sha1 from now() and the users's ID"""
        import hashlib
        import time

        return hashlib.sha1(
            (str(time.monotonic_ns()) + "|" + str(self.user.id)).encode("utf-8")
        ).hexdigest()


class Vote(models.Model):
    """
    Represents a vote for a photo entry.

    The same user can vote several times on the same entry, but only the last
    vote is taken into account.
    """

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"

    # the user who voted, can be none if user is anonymous
    user = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    # the tn session we set with SessionMiddleware
    tn_session_id = models.CharField(max_length=200, blank=True, null=True)
    # the photo entry that was voted for
    photo_entry = models.ForeignKey(PhotoEntry, on_delete=models.PROTECT)
    # the date and time of the vote
    timestamp = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="Date du vote",
        auto_now_add=True,
    )
    # A vote in favor of an entry is (True) or against (False) or Pending (None)
    vote_value = models.BooleanField(null=False, blank=False)
    # If the user is logged in or succeeded in the captcha, we set this to True
    # In case the captcha failed, we set this to False
    captcha_succeeded = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return (
            f"{self.user.username if self.user else 'Anonymous'} -"
            f" {self.photo_entry} - {self.vote_value}"
        )
