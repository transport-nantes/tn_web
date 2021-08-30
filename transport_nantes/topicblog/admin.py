from django.contrib import admin
from .models import TopicBlogPage, TopicBlogTemplate, TopicBlogItem


class TopicBlogPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class TopicBlogTemplateAdmin(admin.ModelAdmin):
    pass


class TopicBlogItemAdmin(admin.ModelAdmin):
    # Making it read-only allows admins to see its ID
    # By default, non modifyable fields are hidden in admin panel
    readonly_fields = ('pk',)


admin.site.register(TopicBlogPage, TopicBlogPageAdmin)
admin.site.register(TopicBlogTemplate, TopicBlogTemplateAdmin)
admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
