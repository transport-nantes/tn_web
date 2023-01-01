from django.contrib import admin
from .models import MapDefinition, MapLayer, MapContent

# Register your models here.
class GeoplanPageAdmin(admin.ModelAdmin):
    pass


admin.site.register(MapDefinition, GeoplanPageAdmin)
admin.site.register(MapLayer, GeoplanPageAdmin)
admin.site.register(MapContent, GeoplanPageAdmin)
