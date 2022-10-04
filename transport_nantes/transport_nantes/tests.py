from subprocess import run
from unittest import TestCase


class MissingMigrationsTest(TestCase):
    def test_missing_migrations(self):
        result = run(["./manage.py", "makemigrations", "--check", "--dry-run"])
        self.assertEqual(result.returncode, 0, "Missing migrations")
