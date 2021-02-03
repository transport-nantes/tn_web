from django.contrib import admin
from .models import MailingList, MailingListEvent, Petition

admin.site.register(MailingList)
admin.site.register(MailingListEvent)
admin.site.register(Petition)
