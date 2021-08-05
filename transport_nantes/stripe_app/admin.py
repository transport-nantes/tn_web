from django.contrib import admin
from .models import TrackingProgression, Donation


class TrackingProgressionAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "amount_form_done", "donation_form_done", )


class DonationAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "email", "first_name", "last_name", "address",
                       "more_address", "postal_code", "city", "country",
                       "periodicity_months", "amount_centimes_euros",
                       "timestamp")


admin.site.register(TrackingProgression, TrackingProgressionAdmin)
admin.site.register(Donation, DonationAdmin)
