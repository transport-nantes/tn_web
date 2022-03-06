from django.contrib import admin
from .models import TopicBlogItem, TopicBlogEmail, TopicBlogPress


class TopicBlogItemAdmin(admin.ModelAdmin):
    # Making it read-only allows admins to see its ID
    # By default, non modifyable fields are hidden in admin panel
    readonly_fields = ('pk',)


class TopicBlogEmailAdmin(admin.ModelAdmin):
    pass


class TopicBlogPressAdmin(admin.ModelAdmin):
    pass


admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
admin.site.register(TopicBlogEmail, TopicBlogEmailAdmin)
admin.site.register(TopicBlogPress, TopicBlogPressAdmin)
