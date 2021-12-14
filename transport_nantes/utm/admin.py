from django.contrib import admin

from .models import UTM

class UtmAdmin(admin.ModelAdmin):
    list_display = ('base_url', 'source', 'campaign', 'content')
    search_fields = ('source', 'campaign', 'content')

admin.site.register(UTM, UtmAdmin)
