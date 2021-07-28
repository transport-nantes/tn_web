from django.contrib import admin
from .models import TrackingProgression, Donation, Donor


class TrackingProgressionAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "amount_form_done", "donation_form_done", )


class DonorAdmin(admin.ModelAdmin):
    pass


class DonationAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "mode", "donor", "amount")


admin.site.register(TrackingProgression, TrackingProgressionAdmin)
admin.site.register(Donor, DonorAdmin)
admin.site.register(Donation, DonationAdmin)
