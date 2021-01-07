from django.urls import path
from django.conf import settings
from .views_m import *

app_name = 'mailing_list'
urlpatterns = [
    path('inscrire', MailingListSignupM.as_view(), name='list_signup'),
    path('inscrire-captcha', QuickMailingListSignupM.as_view(), name='quick_list_signup'),
]

# For debugging the thankyou template:
if hasattr(settings, 'ROLE') and 'production' != settings.ROLE:
    urlpatterns.append(path('merci', MailingListMerciM.as_view(), name='list_ok'))
