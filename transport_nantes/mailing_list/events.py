from django.contrib.auth.models import User
from django.db.models import Max
from django.db.models import Q

from .models import MailingListEvent


def subscribe_user_to_list(user, mailing_list) -> MailingListEvent:
    """Subscribe user to a mailing list or sign a petition"""

    subscribe = MailingListEvent.objects.create(
        user=user,
        mailing_list=mailing_list,
        event_type=MailingListEvent.EventType.SUBSCRIBE)
    subscribe.save()



def unsubscribe_user_from_list(user, mailing_list) -> MailingListEvent:
    """Unsubscribe  user to a mailing list or unsign
       a petition (the petition is still signed by
       the user if he sign again it will only count
       as one)"""

    unsubscribe = MailingListEvent.objects.create(
        user=user,
        mailing_list=mailing_list,
        event_type=MailingListEvent.EventType.UNSUBSCRIBE)
    unsubscribe.save()


def user_current_state(user, mailing_list):
    """Return user's most current state on the provided mailing list

    Return the most recent event associated with this user in this
    mailing list.

    """
    try:
        the_user = MailingListEvent.objects.filter(
            Q(event_type=MailingListEvent.EventType.SUBSCRIBE) |
            Q(event_type=MailingListEvent.EventType.UNSUBSCRIBE),
            user=user, mailing_list=mailing_list).latest(
                'event_timestamp')
        return the_user
    except MailingListEvent.DoesNotExist:
        return MailingListEvent(
            user=user, mailing_list=mailing_list,
            event_type=MailingListEvent.EventType.UNSUBSCRIBE)


def user_subscribe_count(mailing_list):
    """Return the number of users currently subscribed to the mailing list.

    We want to know how many users are currently subscribed.  Note
    that individual users might subscribe and unsubscribe multiple
    times.  Other (future) events could happen as well.
    """
    user_states = MailingListEvent.objects.filter(
        Q(event_type=MailingListEvent.EventType.SUBSCRIBE) |
        Q(event_type=MailingListEvent.EventType.UNSUBSCRIBE),
        mailing_list=mailing_list).values(
            'user').annotate(latest=Max('event_timestamp'))
    users_subscribed = user_states.filter(
        Q(event_type=MailingListEvent.EventType.SUBSCRIBE)).count()
    return users_subscribed


def subscriber_count(mailing_list):
    """Return the number of users who have signed a petition.

    If we want the number of people who receive notifications on a
    petition, we should use user_subscribe_count().  Signers may
    unsubscribe from notifications, but that doesn't unsign the
    petition.

    """
    user_states = MailingListEvent.objects.filter(
        Q(event_type=MailingListEvent.EventType.SUBSCRIBE),
        mailing_list=mailing_list).values(
            'user').annotate(latest=Max('event_timestamp'))
    users_subscribed = user_states.filter(
        Q(event_type=MailingListEvent.EventType.SUBSCRIBE)).count()
    return users_subscribed
