from django.contrib import admin
from django.contrib.sites.models import Site
from django.db import models

class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'domain', 'name')
    search_fields = ('id', 'domain', 'name')

    def __str__(self):
        return '{domain} ({id})'.format(domain=self.domain, id=self.id)

#admin.site.unregister(Site)
#admin.site.register(Site, SiteAdmin)
