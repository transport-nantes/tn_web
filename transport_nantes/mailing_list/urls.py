from django.urls import path
from .views import (MailingListSignup, QuickMailingListSignup,
                    QuickPetitionSignup, PetitionView, MailingListMerci,
                    MailingListListView, FirstStepQuickMailingListSignup)

app_name = 'mailing_list'
urlpatterns = [
    path('inscrire', MailingListSignup.as_view(),
         name='list_signup'),

    path('etape-un-inscription', FirstStepQuickMailingListSignup.as_view(),
         name='first_step_quick_list_signup'),

    path('petition-captcha', QuickPetitionSignup.as_view(),
         name='quick_petition_signup'),
    path('petition/<slug:petition_slug>/', PetitionView.as_view(
         template_name='mailing_list/petition4.html'),
         name='petition'),

    path('list', MailingListListView.as_view(), name='list_items'),
    path('inscrire-captcha',
         QuickMailingListSignup.as_view(),
         name='quick_list_signup'),
    path('merci', MailingListMerci.as_view(),
         name='list_ok'),
]
