from django.test import TestCase
import datetime
from .utils import make_timed_token, token_valid
from django.contrib.auth.models import User
from mailing_list.models import MailingList
from topicblog.models import TopicBlogEmailSendRecord


class TimedTokenTest(TestCase):

    def test_expiry(self):
        """Test token expiration.

        Test that the token remains valid for the time we expect and
        not after.

        """
        EMAIL = "joe@example.com"
        EXPIRY_MINUTES = 2
        EXPIRY_SECONDS = EXPIRY_MINUTES * 60
        NOW = datetime.datetime.now().timestamp()
        for persisted in [0, 1]:
            token = make_timed_token(EMAIL, EXPIRY_MINUTES, persisted, NOW)
            now_response = token_valid(token, NOW)
            self.assertEqual(now_response[0], EMAIL)
            self.assertEqual(now_response[1], persisted)
            before_response = token_valid(token, NOW + EXPIRY_SECONDS - 1)
            self.assertEqual(before_response[0], EMAIL)
            self.assertEqual(before_response[1], persisted)
            after_response = token_valid(token, NOW + EXPIRY_SECONDS + 1)
            self.assertEqual(after_response[0], None)
            self.assertEqual(after_response[1], 0)

    def test_mailing_list_token(self):
        """Testing the result of make_timed_token with
            mailing parameters and test the result with
            token valid"""
        # Create a User object
        user = User.objects.create_user(username='user',
                                        password='password',
                                        email="duponttesteur@test.fr"
                                        )
        # Create a MailingList object
        mailing_list = MailingList.objects.create(
            mailing_list_name="news1",
            mailing_list_token="token1",
            list_active=True,
        )
        # Create a TopicBlogEmailSendRecord object with a fake id
        tb_send_email_record = TopicBlogEmailSendRecord(
            id=1,
            mailinglist=mailing_list,
            recipient=user
        )

        token = \
            make_timed_token(user.email, 1080, 1234,
                             tb_email_send_record_id=tb_send_email_record.id,)
        now_response = token_valid(token)
        self.assertEqual(now_response[0], user.email)
        self.assertEqual(now_response[1], tb_send_email_record.id)
        self.assertEqual(now_response[2], 1234)
