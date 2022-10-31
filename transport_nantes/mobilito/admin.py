from django.contrib import admin

from mobilito import models


class EventInline(admin.TabularInline):
    model = models.Event
    extra = 0


class MobilitoSessionAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    readonly_fields = ('pk', 'start_timestamp', 'end_timestamp', 'session_sha1')
    list_display = ("user", "location", "start_timestamp",
                    "end_timestamp",)
    list_filter = ("user", "location",
                   ("end_timestamp", admin.EmptyFieldListFilter))
    search_fields = ("user", "location",)


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'timestamp',)

    list_display = ("mobilito_session", "event_type", "timestamp")
    list_filter = ("mobilito_session", "event_type",)
    search_fields = ("mobilito_session", "event_type",)


admin.site.register(models.MobilitoSession, MobilitoSessionAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.MobilitoUser)
