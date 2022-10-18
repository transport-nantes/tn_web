from django.contrib import admin
from .models import PhotoEntry


class PhotoEntryAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

    list_display = ("category", "user", "accepted")
    list_filter = ("category", "user__email", "accepted")
    search_fields = ("category", "user__email")


admin.site.register(PhotoEntry, PhotoEntryAdmin)
