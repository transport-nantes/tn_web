from django.contrib import admin
from .models import MapPage

# Register your models here.
class GeoplanPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(MapPage, GeoplanPageAdmin)