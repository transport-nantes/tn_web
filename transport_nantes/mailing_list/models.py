from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import django.utils.timezone
import uuid

# Create your models here.

class MailingList(models.Model):
    """Represent things a mailing list.
    """
    # This is a user-visible name that can change.
    mailing_list_name = models.CharField(max_length=80, blank=False)
    # This is the unique name that can't change.  It just makes code a
    # bit more readable than referring to the pk id.
    mailing_list_token = models.CharField(max_length=80, blank=False,
                                          unique=True)
    # How often the user should expect to be contacted.
    # Zero means no frequency objective.
    contact_frequency_weeks = models.IntegerField(default=0)
    list_created = models.DateTimeField(default=django.utils.timezone.now)
    # We shouldn't ever delete newsletters, because that would either
    # cascade deletes or lead to dangling foreign keys.  Rather, we
    # should make the newsletter inactive, which should make it not
    # appear in any choice lists and otherwise not be usable.
    list_active = models.BooleanField(default=False)

    def __str__(self):
        print('MailingList')
        return '{name} ({token}) f={freq} semaines'.format(
            name=self.mailing_list_name,
            token=self.mailing_list_token,
            freq=self.contact_frequency_weeks)

class MailingListEvent(models.Model):
    """Events on mailing lists.

    This represents subscribes, unsubscribes, and bounces.  We'd like
    to understand what happens and when, not just the current state of
    the system.

    """
    class EventType(models.TextChoices):
        SUBSCRIBE = 'sub', 'inscription'
        UNSUBCRIBE = 'unsub', 'désinscription'
        BOUNCE = 'bounce', 'bounce'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mailing_list = models.ForeignKey(MailingList,
                                     on_delete=models.CASCADE)
    event_timestamp = models.DateTimeField(default=django.utils.timezone.now)
    event_type = models.CharField(max_length=6, choices=EventType.choices)

    def __str__(self):
        return 'U={user}, L={mlist}, E={event}, {ts}'.format(
            user=self.user, mlist=self.mailing_list,
            event=self.event_type, ts=self.event_timestamp)

# For actually sending emails, we'll want another class for that.  It
# should provide a template name and text to fill the template.  The
# rendered template should then provide a link to a page that displays
# the page.  This is all a bit like the ClusterBlog class.

# We'll need to make sure we have an automatic unsubscribe pathway
# with link in mails.

