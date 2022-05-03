from django.contrib import admin
from .models import (TopicBlogItem, TopicBlogEmail, TopicBlogEmailSendRecord,
                     TopicBlogPress, TopicBlogLauncher,
                     TopicBlogMailingListPitch, TopicBlogEmailClicks)


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


class TopicBlogMailingListPitchAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

    list_display = ("title", "slug", "mailing_list")
    list_filter = ("title", "slug", "mailing_list")
    search_fields = ("title", "slug", "mailing_list")


class TopicBlogEmailClicksAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

    list_display = ("email", "click_url", "click_time")
    list_filter = ("email", "click_time")
    search_fields = ("email", "click_url", "click_time")


admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
admin.site.register(TopicBlogEmail, TopicBlogEmailAdmin)
admin.site.register(TopicBlogPress, TopicBlogPressAdmin)
admin.site.register(TopicBlogLauncher, TopicBlogLauncherAdmin)
admin.site.register(TopicBlogEmailSendRecord, TopicBlogEmailSendRecordAdmin)
admin.site.register(TopicBlogMailingListPitch, TopicBlogMailingListPitchAdmin)
admin.site.register(TopicBlogEmailClicks, TopicBlogEmailClicksAdmin)
