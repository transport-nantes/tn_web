from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=80, blank=True)
    email_confirmed = models.BooleanField(default=False)
    authenticates_by_mail = models.BooleanField(default=True)

    def __str__(self):
        if self.email_confirmed:
            confirmed = "email confirmed"
        else:
            confirmed = "confirmation pending"
        if self.authenticates_by_mail:
            auth = "authenticates by mail"
        else:
            auth = "authenticates by password"
        return '{email}/[{uid}] / {conf} / {auth}'.format(
            email=self.user.email,
            uid=self.user.pk,
            conf=confirmed, auth=auth)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
