from django.test import TestCase
import datetime

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
        k_now = datetime.datetime.now().timestamp()
        for persisted in [0, 1]:
            token = make_timed_token(k_email, k_expiry_minutes,
                                     persisted, k_now)
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
