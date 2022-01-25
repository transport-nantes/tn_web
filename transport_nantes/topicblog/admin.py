from django.contrib import admin
from .models import (TopicBlogTemplate, TopicBlogItem,
                     TopicBlogEmail)


class TopicBlogTemplateAdmin(admin.ModelAdmin):
    pass


class TopicBlogItemAdmin(admin.ModelAdmin):
    # Making it read-only allows admins to see its ID
    # By default, non modifyable fields are hidden in admin panel
    readonly_fields = ('pk',)


class TopicBlogEmailAdmin(admin.ModelAdmin):
    pass


admin.site.register(TopicBlogTemplate, TopicBlogTemplateAdmin)
admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
admin.site.register(TopicBlogEmail, TopicBlogEmailAdmin)
