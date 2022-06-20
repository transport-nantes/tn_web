from django.contrib import admin
from .models import (TopicBlogItem, TopicBlogEmail, SendRecordMarketingEmail,
                     TopicBlogPress, TopicBlogLauncher,
                     TopicBlogMailingListPitch, SendRecordMarketingPress,
                     SendRecordTransactionalPress,
                     SendRecordTransactionalEmail,
                     SendRecordTransactionalAdHoc,
                     )


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


class SendRecordMarketingEmailAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'send_time',)

    list_display = ("mailinglist", "recipient", "send_time", "slug")
    list_filter = ("mailinglist", "recipient", "send_time", "slug")
    search_fields = ("mailinglist", "recipient", "send_time", "slug")


class SendRecordMarketingPressAdmin(admin.ModelAdmin):
    readonly_fields = ('pk', 'send_time',)

    list_display = ("mailinglist", "recipient", "send_time", "slug")
    list_filter = ("mailinglist", "recipient", "send_time", "slug")
    search_fields = ("mailinglist", "recipient", "send_time", "slug")


class TopicBlogMailingListPitchAdmin(admin.ModelAdmin):
    readonly_fields = ('pk',)

    list_display = ("title", "slug", "mailing_list")
    list_filter = ("title", "slug", "mailing_list")
    search_fields = ("title", "slug", "mailing_list")


admin.site.register(TopicBlogItem, TopicBlogItemAdmin)
admin.site.register(TopicBlogEmail, TopicBlogEmailAdmin)
admin.site.register(TopicBlogPress, TopicBlogPressAdmin)
admin.site.register(TopicBlogLauncher, TopicBlogLauncherAdmin)
admin.site.register(SendRecordMarketingEmail, SendRecordMarketingEmailAdmin)
admin.site.register(TopicBlogMailingListPitch, TopicBlogMailingListPitchAdmin)
admin.site.register(SendRecordMarketingPress, SendRecordMarketingPressAdmin)
admin.site.register(SendRecordTransactionalEmail)
admin.site.register(SendRecordTransactionalPress)
admin.site.register(SendRecordTransactionalAdHoc)
