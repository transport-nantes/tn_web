from django.contrib import admin

from mobilito import models


class EventInline(admin.TabularInline):
    model = models.Event
    extra = 0


class SessionAdmin(admin.ModelAdmin):
    inlines = [EventInline]
    readonly_fields = ('pk', 'start_timestamp', 'end_timestamp',)

    list_display = ("user", "address", "city", "postcode", "start_timestamp",
                    "end_timestamp",)
    list_filter = ("user", "address", "city", "postcode",
                   ("end_timestamp", admin.EmptyFieldListFilter))
    search_fields = ("user", "address", "city", "postcode",)


class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'timestamp',)

    list_display = ("session", "type", "timestamp")
    list_filter = ("session", "type",)
    search_fields = ("session", "type",)


admin.site.register(models.Session, SessionAdmin)
admin.site.register(models.Event, EventAdmin)
