from django.contrib import admin
from .models import TrackingProgression

# Register your models here.
class TrackingProgressionAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "step_1", "step_2", )

admin.site.register(TrackingProgression, TrackingProgressionAdmin)
