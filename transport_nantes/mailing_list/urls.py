from django.urls import path

from . import views

app_name = 'mailing_list'
urlpatterns = [
    path('inscrire', views.MailingListSignup.as_view(), name='list_signup'),
    # For debugging the thankyou template:
    path('merci', views.MailingListMerci.as_view(), name='list_ok'),
]
