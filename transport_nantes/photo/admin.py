from django.contrib import admin
from .models import PhotoEntry, Vote


class PhotoEntryAdmin(admin.ModelAdmin):
    readonly_fields = ("pk", "sha1_name")

    list_display = ("category", "user", "accepted")
    list_filter = ("category", "accepted")
    search_fields = ("category", "user__email", "sha1_name")


admin.site.register(PhotoEntry, PhotoEntryAdmin)
admin.site.register(Vote)
