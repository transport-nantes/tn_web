from typing import Union
from django.contrib.auth.models import User
from django.db.models import OuterRef, Subquery
from .models import PhotoEntry, Vote


def get_user_vote(
        user: 'User',
        photo_entry: 'PhotoEntry',
        tn_session_id: str = None) -> Union['Vote', None]:
    """
    Returns the the user's last vote for the given photo entry.
    """
    # Check if the user isn't anonymous
    if user.is_authenticated:
        return Vote.objects.filter(
            user=user, photo_entry=photo_entry, captcha_succeeded=True
            ).order_by("timestamp").last()
    elif tn_session_id:
        return Vote.objects.filter(
            tn_session_id=tn_session_id,
            photo_entry=photo_entry,
            captcha_succeeded=True
            ).order_by("timestamp").last()


def get_number_of_upvotes(photo_entry: 'PhotoEntry') -> int:
    """
    Returns the number of upvotes for the given photo entry.
    """
    upvoting_users = User.objects.annotate(
        latest_action=Subquery(
            Vote.objects.filter(
                photo_entry=photo_entry,
                user=OuterRef('pk'),
                captcha_succeeded=True,
            ).order_by('-timestamp').values("vote_value")[:1]
        )
    ).filter(latest_action=True).count()
    return upvoting_users


def get_number_of_downvotes(photo_entry: 'PhotoEntry') -> int:
    """
    Returns the number of downvotes for the given photo entry.
    """
    downvoting_users = User.objects.annotate(
        latest_action=Subquery(
            Vote.objects.filter(
                photo_entry=photo_entry,
                user=OuterRef('pk'),
                captcha_succeeded=True,
            ).order_by('-timestamp').values("vote_value")[:1]
        )
    ).filter(latest_action=False).count()
    return downvoting_users
