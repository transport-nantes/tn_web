from django.contrib import admin

from .models import UTM


class UtmAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "timestamp",
        "ua_is_bot",
        "source",
        "campaign",
        "content",
        "base_url",
    )
    search_fields = ("source", "campaign", "content", "base_url", "session_id")


admin.site.register(UTM, UtmAdmin)
