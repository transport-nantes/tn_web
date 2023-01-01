from django.test import TestCase
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import make_aware

from .events import *
from .models import MailingList, MailingListEvent


class EventsTest(TestCase):
    def setUp(self):
        User.objects.create(username="Alice")
        User.objects.create(username="Bob")
        MailingList.objects.create(mailing_list_token="dog", list_active=True)
        MailingList.objects.create(mailing_list_token="cat", list_active=True)
        self.base_time = make_aware(datetime.datetime.now())

    def test_user_current_state(self):
        alice = User.objects.get(username="Alice")
        bob = User.objects.get(username="Bob")
        dog_list = MailingList.objects.get(mailing_list_token="dog")
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(1),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(3),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(5),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        self.assertEqual(
            user_current_state(alice, dog_list).event_type,
            MailingListEvent.EventType.SUBSCRIBE,
        )
        self.assertEqual(
            user_current_state(bob, dog_list).event_type,
            MailingListEvent.EventType.SUBSCRIBE,
        )
        # Unsubscribe Bob but not Alice.
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(4),
            event_type=MailingListEvent.EventType.UNSUBSCRIBE,
        )
        self.assertEqual(
            user_current_state(alice, dog_list).event_type,
            MailingListEvent.EventType.SUBSCRIBE,
        )
        self.assertEqual(
            user_current_state(bob, dog_list).event_type,
            MailingListEvent.EventType.UNSUBSCRIBE,
        )
        # Check behaviour for other lists.
        cat_list = MailingList.objects.get(mailing_list_token="cat")
        self.assertEqual(
            user_current_state(alice, cat_list).event_type,
            MailingListEvent.EventType.UNSUBSCRIBE,
        )

    def test_user_subscribe_count(self):
        alice = User.objects.get(username="Alice")
        bob = User.objects.get(username="Bob")
        cat_list = MailingList.objects.get(mailing_list_token="cat")
        dog_list = MailingList.objects.get(mailing_list_token="dog")
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(1),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(3),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=cat_list,
            event_timestamp=self.base_time,
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=cat_list,
            event_timestamp=self.base_time,
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=cat_list,
            event_timestamp=self.base_time + datetime.timedelta(5),
            event_type=MailingListEvent.EventType.UNSUBSCRIBE,
        )
        self.assertEqual(user_subscribe_count(dog_list), 2)
        self.assertEqual(user_subscribe_count(cat_list), 1)

    def test_subscriber_count(self):
        alice = User.objects.get(username="Alice")
        bob = User.objects.get(username="Bob")
        cat_list = MailingList.objects.get(mailing_list_token="cat")
        dog_list = MailingList.objects.get(mailing_list_token="dog")
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(1),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(3),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        MailingListEvent.objects.create(
            user=alice,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(5),
            event_type=MailingListEvent.EventType.SUBSCRIBE,
        )
        self.assertEqual(subscriber_count(dog_list), 2)
        self.assertEqual(subscriber_count(cat_list), 0)

        # Unsubscribe Bob but not Alice.
        MailingListEvent.objects.create(
            user=bob,
            mailing_list=dog_list,
            event_timestamp=self.base_time + datetime.timedelta(4),
            event_type=MailingListEvent.EventType.UNSUBSCRIBE,
        )
        self.assertEqual(subscriber_count(dog_list), 2)
        self.assertEqual(subscriber_count(cat_list), 0)
