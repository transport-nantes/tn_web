from django.contrib import admin
from .models import PhotoEntry


class PhotoEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

    list_display = ("category", "user")
    list_filter = ("category", "user")
    search_fields = ("category", "user")


admin.site.register(PhotoEntry, PhotoEntryAdmin)
