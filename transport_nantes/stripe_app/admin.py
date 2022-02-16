from django.contrib import admin
from .models import TrackingProgression, Donation


class TrackingProgressionAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        """Makes read only all fields of the model."""
        return False


class DonationAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        """Makes read only all fields of the model."""
        return False
    readonly_fields = ("timestamp",)

    class Meta:
        list_display = [field.name for field in Donation._meta.get_fields()]


admin.site.register(TrackingProgression, TrackingProgressionAdmin)
admin.site.register(Donation, DonationAdmin)
