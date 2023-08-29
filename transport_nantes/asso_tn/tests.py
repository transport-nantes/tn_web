from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from .utils import make_timed_token, token_valid


class TimedTokenTest(TestCase):
    def test_expiry(self):
        """Test token expiration.

        Test that the token remains valid for the time we expect and
        not after.

        """
        k_email = "joe@example.com"
        k_expiry_minutes = 2
        k_expiry_seconds = k_expiry_minutes * 60
        k_now = datetime.now(timezone.utc).timestamp()
        for persisted in [0, 1]:
            token = make_timed_token(
                k_email, k_expiry_minutes, persisted, k_now
            )
            now_response = token_valid(token, k_now)
            self.assertEqual(now_response[0], k_email)
            self.assertEqual(now_response[1], persisted)
            before_response = token_valid(token, k_now + k_expiry_seconds - 1)
            self.assertEqual(before_response[0], k_email)
            self.assertEqual(before_response[1], persisted)
            after_response = token_valid(token, k_now + k_expiry_seconds + 1)
            self.assertEqual(after_response[0], None)
            self.assertEqual(after_response[1], 0)


class TestIndex(TestCase):
    def test_index_page(self):
        """Test the new index page.

        This is far too rudimentary.  We should improve it some day,
        such as before we make it the default index page.

        """
        response = self.client.get("/index2")
        self.assertEqual(response.status_code, 200)


class PreferencesViewTests(TestCase):
    """Test the preferences view."""

    def setUp(self):
        self.user = User.objects.create_user(username="foobar", password="bar")
        self.auth_client = Client()
        self.auth_client.login(username=self.user.username, password="bar")

    def test_preferences_view(self):
        """Test the preferences view."""
        # Check the status code for anon users
        response = self.client.get(reverse_lazy("asso_tn:preferences"))
        self.assertRedirects(
            response,
            reverse_lazy("authentication:login")
            + "?next="
            + reverse_lazy("asso_tn:preferences"),
        )

        # Check the status code for logged in users
        response = self.auth_client.get(reverse_lazy("asso_tn:preferences"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

        # Change the username
        new_name = "abc"
        self.auth_client.post(
            reverse(
                "asso_tn:edit_username",
                args=[self.user.username],
            ),
            data={"username": new_name},
        )
        # Refresh the user object
        self.user.refresh_from_db()

        # Check that the username has been changed
        response = self.auth_client.get(reverse_lazy("asso_tn:preferences"))
        self.assertContains(response, new_name)
        # Check that the old username is not present
        self.assertNotContains(response, "foobar")

        # Check that we're redirected to login if attempting to POST while
        # not logged in
        response = self.client.post(
            reverse(
                "asso_tn:edit_username",
                args=[self.user.username],
            ),
            data={"username": "foobazbar"},
        )
        self.assertRedirects(
            response,
            reverse_lazy("authentication:login")
            + "?next="
            + reverse(
                "asso_tn:edit_username",
                args=[self.user.username],
            ),
        )

        # Check that we're not allowed to use GET on edit_username
        response = self.auth_client.get(
            reverse(
                "asso_tn:edit_username",
                args=[self.user.username],
            ),
        )
        self.assertEqual(response.status_code, 405)

        # Check that we can't have duplicates usernames
        self.user_2 = User.objects.create_user(
            username="test-2", password="bar"
        )
        self.auth_client.force_login(self.user)
        response = self.auth_client.post(
            reverse(
                "asso_tn:edit_username",
                args=[self.user.username],
            ),
            data={"username": self.user_2.username},
            follow=True,
        )
        self.assertContains(response, self.user.username)
        self.assertNotContains(response, self.user_2.username)
