from django.contrib import admin
from .models import MapPage

# Register your models here.
class GeoplanPageAdmin(admin.ModelAdmin):
    pass

admin.site.register(MapPage, GeoplanPageAdmin)