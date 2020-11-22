from django.contrib import admin
from .models import MailingList, MailingListEvent

admin.site.register(MailingList)
admin.site.register(MailingListEvent)
