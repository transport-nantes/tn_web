from django.contrib import admin
from .models import MailingList, MailingListEvent, Petition
from .forms import MailingListAdminForm


class MailingListAdmin(admin.ModelAdmin):
    form = MailingListAdminForm


admin.site.register(MailingList, MailingListAdmin)
admin.site.register(MailingListEvent)
admin.site.register(Petition)
