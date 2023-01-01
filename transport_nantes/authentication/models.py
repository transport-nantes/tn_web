from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Rather than insisting the user invent a unique user name, we
    # courteously create the username for the user, set it to a random
    # value, and initially set the display_name to the part before the
    # "@" in the email.  The user can change the display name and
    # email as s/he sees fit.
    display_name = models.CharField(max_length=80, blank=True)
    email_confirmed = models.BooleanField(default=False)
    # We'll set this to False if the user provides a password.  If
    # it's true, we should have initialised the password to something
    # random.  (This is why we don't abandon it altogether and just
    # check the password.)
    authenticates_by_mail = models.BooleanField(default=True)

    # We would like to know something about where people think of
    # themselves as being attached to.  Note that this is quite
    # different from where they actually connect from.
    commune = models.CharField(max_length=100, blank=True)
    code_postal = models.CharField(max_length=10, blank=True)

    def __str__(self):
        if self.email_confirmed:
            confirmed = "email confirmed"
        else:
            confirmed = "confirmation pending"
        if self.authenticates_by_mail:
            auth = "authenticates by mail"
        else:
            auth = "authenticates by password"
        return "{email}/[{uid}] / {conf} / {auth} ({commune}, {cp})".format(
            email=self.user.email,
            uid=self.user.pk,
            conf=confirmed,
            auth=auth,
            commune=self.commune,
            cp=self.code_postal,
        )


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
