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
        token = make_timed_token(USER_ID, EXPIRY_MINUTES, NOW)
        self.assertEqual(token_valid(token, NOW), USER_ID)
        self.assertEqual(token_valid(token, NOW + EXPIRY_SECONDS - 1), USER_ID)
        self.assertEqual(token_valid(token, NOW + EXPIRY_SECONDS + 1), -1)
