from django.contrib import admin
from .models import TrackingProgression, Donation


class TrackingProgressionAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        """Makes read only all fields of the model."""
        return False


class DonationAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "email", "first_name", "last_name", "address",
                       "more_address", "postal_code", "city", "country",
                       "periodicity_months", "amount_centimes_euros",
                       "timestamp")


admin.site.register(TrackingProgression, TrackingProgressionAdmin)
admin.site.register(Donation, DonationAdmin)
