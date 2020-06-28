from django.db import models

class Observatoire(models.Model):
    """Represent an observatoire.

    """
    # A human-presentable name of the observatoire.
    name = models.CharField(max_length=100)
    # More information about the observatoire.  Also for humans.
    description = models.TextField()

    # The active field is used in the name (to help us pick fields
    # that are active).  Eventually we might use it to avoid
    # automatically showing old observatoires.
    active = models.BooleanField(default=True)

    # 
    # intro_text = models.TextField()

    def __str__(self):
        active = '+' if self.active else '-'
        return '{act}{name}'.format(
            act=active, name=self.name)

#class Observatoire
