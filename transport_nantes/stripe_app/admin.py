from django.contrib import admin
from .models import TrackingProgression, Donation, Donator


class TrackingProgressionAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "amount_form_done", "donation_form_done", )


class DonatorAdmin(admin.ModelAdmin):
    pass


class DonationAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "mode", "donator", "amount")


admin.site.register(TrackingProgression, TrackingProgressionAdmin)
admin.site.register(Donator, DonatorAdmin)
admin.site.register(Donation, DonationAdmin)
