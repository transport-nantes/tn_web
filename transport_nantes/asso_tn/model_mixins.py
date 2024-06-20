"""Copyright 2024  Français pour une Meilleure Mobilité."""

import logging

from django.db import IntegrityError, transaction
from django.utils.crypto import get_random_string

logger = logging.getLogger("django")


K_SAVE_RETRY_MAX_COUNT = 10  # Avoid infinite loops.


def get_or_none(classmodel, **kwargs):
    """Get an object, return None if not found.

    Usage:

      my_object = get_or_none(MyModel, my_field="my_value")
    """
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        logger.warning(
            f"get_or_none: {classmodel} does not exist, kwargs={kwargs}"
        )
        return None


class UniqueIdentifierMixin:
    identifier_field_name = "identifier"  # Default identifier field name.
    identifier_field_length = 20  # Default identifier field length.

    def generate_unique_identifier(self):
        """Create a new unique identifier.

        Subclasses should override this method if they want to do
        something different.

        """
        return get_random_string(self.identifier_field_length)

    def requires_identifier(self):
        """Return true if an identifier is required.

        Subclasses should override this method if they need additional
        logic before generating an identifier.

        """
        return True

    def save(self, *args, **kwargs):
        if (
            self.requires_identifier()
            and not getattr(self, self.identifier_field_name)
            and not self.id
        ):
            setattr(
                self,
                self.identifier_field_name,
                self.generate_unique_identifier(),
            )
        for _ in range(K_SAVE_RETRY_MAX_COUNT):
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError as integrity_err:
                # Only handle IntegrityErrors related to identifier.
                if self.identifier_field_name not in str(integrity_err):
                    raise integrity_err
                logger.warning(
                    "Unexpectedly generated duplicate"
                    f" {self.identifier_field_name}"
                    f" {getattr(self, self.identifier_field_name)}:"
                    f" {integrity_err}"
                )
                if self.id:
                    logger.error(
                        f"Unexpected IntegrityError after save:"
                        f" {integrity_err}"
                    )
                    raise integrity_err
                new_identifier = self.generate_unique_identifier()
                logger.warning(
                    f"Resetting {self.identifier_field_name} from"
                    f" {getattr(self, self.identifier_field_name)}"
                    f" to {new_identifier}"
                )
                setattr(self, self.identifier_field_name, new_identifier)
        else:
            raise ValueError(
                "Max retries for generating a unique"
                f" {self.identifier_field_name}."
            )
