from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone

# This application might have been called newsletter.  Think of this
# as about newsletters, not about the lists, in the sense that this is
# an application that is designed for keeping in touch with lists of
# people, currently by email.


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

    # Is this list a petition?  The difference is only the minds of
    # the humans.  To a human, a petition is something you sign in
    # order to support something.  A mailing list is something you
    # subscribe to in order to receive news.
    #
    # To us, they are both something that you link your user id to in
    # order because you have an interest in something.  Privacy laws
    # pretty much prevent us from telling anyone who signed anyway.
    is_petition = models.BooleanField(default=False)

    def __str__(self):
        return '{name} ({token}) f={freq} semaines'.format(
            name=self.mailing_list_name,
            token=self.mailing_list_token,
            freq=self.contact_frequency_weeks)


class Petition(models.Model):
    """Parameters of a petition.

    A petition is a wrapper on top of a mailing list.  The petition
    object codifies the text and other presentation details of the
    petition.  The underlying mailing list is the set of signers.

    Signers can unsubscribe from notices, in which case we shouldn't
    mail them anymore.  We don't currently support a concept of "I
    didn't sign this", though perhaps we eventually should (but only
    in the signing confirmation mail).

    """
    mailing_list = models.ForeignKey(MailingList,
                                     on_delete=models.CASCADE)
    # How we'll identify this petition on our website.
    slug = models.SlugField(max_length=70, allow_unicode=True,
                            blank=False, unique=True)
    petition1_md = models.TextField(blank=False)
    petition2_md = models.TextField(blank=True)
    petition3_md = models.TextField(blank=True)
    petition4_md = models.TextField(blank=True)

    # Social media.
    meta_description = models.TextField(blank=True)
    twitter_title = models.CharField(max_length=80, blank=True)
    twitter_description = models.TextField(blank=True)
    twitter_image = models.CharField(max_length=100, blank=True)

    og_title = models.CharField(max_length=80, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.CharField(max_length=100, blank=True)

    def set_context(self, context):
        """Set context that the model can provide.

        """
        social = {}
        social['twitter_title'] = self.twitter_title
        social['twitter_description'] = self.twitter_description
        social['twitter_image'] = self.twitter_image

        social['og_title'] = self.og_title
        social['og_description'] = self.og_description
        social['og_image'] = self.og_image

        context['social'] = social

    def __str__(self):
        return '{sl}  ->  ({list_name})'.format(
            sl=self.slug,
            list_name=self.mailing_list.mailing_list_name)


class MailingListEvent(models.Model):
    """Events on mailing lists.

    This represents subscribes, unsubscribes, and bounces.  We'd like
    to understand what happens and when, not just the current state of
    the system.

    """
    class EventType(models.TextChoices):
        SUBSCRIBE = 'sub', 'inscription'
        UNSUBSCRIBE = 'unsub', 'désinscription'
        BOUNCE = 'bounce', 'bounce'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mailing_list = models.ForeignKey(MailingList,
                                     on_delete=models.CASCADE)
    event_timestamp = models.DateTimeField(default=django.utils.timezone.now)
    event_type = models.CharField(max_length=6, choices=EventType.choices)

    def __str__(self):
        return 'U={u_fn} {u_ln} <{u_e}> ({u_commune}), L={mlist}, E={event}, {ts}'.format(
            u_fn=self.user.first_name,
            u_ln=self.user.last_name,
            u_e=self.user.email,
            u_commune=self.user.profile.commune,
            mlist=self.mailing_list,
            event=self.event_type, ts=self.event_timestamp)

# For actually sending emails, we'll want another class for that.  It
# should provide a template name and text to fill the template.  The
# rendered template should then provide a link to a page that displays
# the page.  This is all a bit like the ClusterBlog class.

# We'll need to make sure we have an automatic unsubscribe pathway
# with link in mails.
