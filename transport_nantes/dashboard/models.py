from django.db import models


class DashboardPermissions(models.Model):
    """Model to store permissions for dashboard."""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("dashboard.may_see", "May see dashboard"),
        )
