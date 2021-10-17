from django.contrib import admin
from .models import TopicBlogPage
from .models import TopicBlogContentType, TopicBlogTemplate, TopicBlogItem


class TopicBlogPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class TopicBlogTemplateAdmin(admin.ModelAdmin):
    pass


class TopicBlogItemAdmin(admin.ModelAdmin):
    # Making it read-only allows admins to see its ID
    # By default, non modifyable fields are hidden in admin panel
    readonly_fields = ('pk',)

class TopicBlogContentTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(TopicBlogContentType, TopicBlogContentTypeAdmin)
admin.site.register(TopicBlogPage, TopicBlogPageAdmin)
admin.site.register(TopicBlogTemplate, TopicBlogTemplateAdmin)
admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
