from django.urls import path
from django.conf import settings
from . import views

app_name = 'mailing_list'
urlpatterns = [
    path('inscrire', views.MailingListSignup.as_view(), name='list_signup'),
]

# For debugging the thankyou template:
if hasattr(settings, 'ROLE') and 'production' != settings.ROLE:
    urlpatterns.append(path('merci', views.MailingListMerci.as_view(), name='list_ok'))
