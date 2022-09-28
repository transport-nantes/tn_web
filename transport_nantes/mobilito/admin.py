from django.contrib import admin

from mobilito import models


class EventInline(admin.TabularInline):
    model = models.Event
    extra = 0


class SessionAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    readonly_fields = ('pk', 'start_timestamp', 'end_timestamp', 'session_sha1')
    list_display = ("user", "location", "start_timestamp",
                    "end_timestamp",)
    list_filter = ("user", "location",
                   ("end_timestamp", admin.EmptyFieldListFilter))
    search_fields = ("user", "location",)


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'timestamp',)

    list_display = ("session", "event_type", "timestamp")
    list_filter = ("session", "event_type",)
    search_fields = ("session", "event_type",)


admin.site.register(models.Session, SessionAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.MobilitoUser)
