from django.db import models

# The observatoire models were designed for watching elected officials
# and their actions.  This is probably not sufficiently generalised
# for anything else, which is why, say, the Observatoire du
# Velopolitain needs to be its own application with its own data
# models.
#
# There's a tricky question about repeating officials from one
# observatoire to the next.  It seems worth requiring re-entry because
# (1) they may have different roles (e.g., city and metropole) with
# different contact information, and (2) as time passes they may
# simply change roles.

class Observatoire(models.Model):
    """Represent an observatoire.

    """
    # A human-presentable name of the observatoire.
    name = models.CharField(max_length=100)
    # More information about the observatoire.  Also for humans.
    description = models.TextField()

    # The day on which this observatoire starts.
    start_date = models.DateField()

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

class ObservatoirePerson(models.Model):
    """Represent a person being observed.

    This would typically be an elected official in the context that
    we've constructed this application.

    """
    # See the remark at the top of the file about why we would assign
    # people to observatoires and so maybe repeat them.
    observatoire = models.ForeignKey(Observatoire, on_delete=models.CASCADE)

    # In a self-service context, we'll use validated to indicate that
    # we've confirmed that the person is authorised to reply for the
    # list.
    validated = models.BooleanField()

    # The name of the person and the entity to which they belong.  The
    # entity is probably a commune, department, or region.
    person_name = models.CharField(max_length=100)
    entity = models.CharField(max_length=100)

    # Contact and tagging info.
    email = models.CharField(max_length=100, blank=True)
    # The twitter field is the part after the "@".
    twitter = models.CharField(max_length=100, blank=True)
    # The facebook username, after the "/" in the page URL.
    facebook = models.CharField(max_length=100, blank=True)
