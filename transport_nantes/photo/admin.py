from django.contrib import admin
from .models import PhotoEntry

class PhotoEntryAdmin(admin.ModelAdmin):
    pass


admin.site.register(PhotoEntry, PhotoEntryAdmin)
