"""Copyright 2024  Français pour une Meilleure Mobilité."""

from django.db import models
from django.test import TestCase

from asso_tn.model_mixins import UniqueIdentifierMixin


class DummyModel(UniqueIdentifierMixin, models.Model):
    """Dummy model for testing UniqueIdentifierMixin."""

    identifier = models.CharField(max_length=50, unique=True)
    dummy_flag = models.BooleanField(default=True)

    def requires_identifier(self):
        return self.dummy_flag


class UniqueIdentifierMixinTest(TestCase):
    """Test UniqueIdentifierMixin.

    Note that settings.py must have the following configuration
    (which, if I understand correctly, is only read at django startup,
    which is why we can't use @override_settings to do the same):

    if "test" in sys.argv:
        MIGRATION_MODULES = {"asso_tn": "asso_tn.test_unique_mixin"}

    """

    def test_identifier_is_generated_on_save(self):
        instance = DummyModel()
        instance.save()
        self.assertTrue(instance.identifier)

    def test_identifier_is_not_generated_if_not_required(self):
        instance = DummyModel(dummy_flag=False)
        instance.save()
        self.assertFalse(instance.identifier)

    def test_save_handles_duplicate_identifiers(self):
        # Manually create a model with an identifier
        identifier = "test-identifier"
        DummyModel.objects.create(identifier=identifier)

        # Attempt to save another instance with the same identifier
        # and ensure that the mixin handles the duplication
        instance = DummyModel()
        instance.identifier = identifier
        instance.save()
        self.assertNotEqual(instance.identifier, identifier)

    def test_max_retries_raised(self):
        # Override the generate_random_identifier function to always
        # return the same value
        original_func = DummyModel.generate_unique_identifier

        DummyModel.generate_unique_identifier = lambda x: "constant_value"
        DummyModel.objects.create(identifier="constant_value")

        instance = DummyModel()

        with self.assertRaises(ValueError) as context:
            instance.save()

        self.assertTrue(
            "Max retries for generating a unique identifier"
            in str(context.exception)
        )

        # Reset the function back to its original
        DummyModel.generate_unique_identifier = original_func
