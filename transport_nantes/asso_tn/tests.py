from django.test import TestCase
import datetime

from .utils import make_timed_token, token_valid

# Create your tests here.

class TimedTokenTest(TestCase):

    def test_expiry(self):
        """Test token expiration.

        Test that the token remains valid for the time we expect and
        not after.

        """
        USER_ID = 3
        EXPIRY_MINUTES = 2
        EXPIRY_SECONDS = EXPIRY_MINUTES * 60
        NOW = datetime.datetime.now().timestamp()
        for persisted in [0, 1]:
            token = make_timed_token(USER_ID, EXPIRY_MINUTES, persisted, NOW)
            now_response = token_valid(token, NOW)
            self.assertEqual(now_response[0], USER_ID)
            self.assertEqual(now_response[1], persisted)
            before_response = token_valid(token, NOW + EXPIRY_SECONDS - 1)
            self.assertEqual(before_response[0], USER_ID)
            self.assertEqual(before_response[1], persisted)
            after_response = token_valid(token, NOW + EXPIRY_SECONDS + 1)
            self.assertEqual(after_response[0], -1)
            self.assertEqual(after_response[1], 0)
