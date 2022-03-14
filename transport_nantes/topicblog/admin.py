from django.contrib import admin
from .models import (TopicBlogItem, TopicBlogEmail, TopicBlogEmailSendRecord,
                     TopicBlogPress, TopicBlogLauncher)


class TopicBlogItemAdmin(admin.ModelAdmin):
    # Making it read-only allows admins to see its ID
    # By default, non modifyable fields are hidden in admin panel
    readonly_fields = ('pk',)


class TopicBlogEmailAdmin(admin.ModelAdmin):
    pass


class TopicBlogPressAdmin(admin.ModelAdmin):
    pass


class TopicBlogLauncherAdmin(admin.ModelAdmin):
    pass


class TopicBlogEmailSendRecordAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'send_time',)

    list_display = ("mailinglist", "recipient", "send_time", "slug")
    list_filter = ("mailinglist", "recipient", "send_time", "slug")
    search_fields = ("mailinglist", "recipient", "send_time", "slug")


admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
admin.site.register(TopicBlogEmail, TopicBlogEmailAdmin)
admin.site.register(TopicBlogPress, TopicBlogPressAdmin)
admin.site.register(TopicBlogLauncher, TopicBlogLauncherAdmin)
admin.site.register(TopicBlogEmailSendRecord, TopicBlogEmailSendRecordAdmin)
