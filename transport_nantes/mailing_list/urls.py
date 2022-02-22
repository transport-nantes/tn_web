from django.urls import path
from django.conf import settings
from .views import (MailingListSignup, QuickMailingListSignup,
                    QuickPetitionSignup, PetitionView, MailingListMerci,
                    MailingListListView, FirstStepQuickMailingListSignup,
                    UserStatusView, MailingListSubscribeFromStatus,
                    MailingListUnsubscribeFromStatus)

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
    path('status', UserStatusView.as_view(), name='user_status'),
    path('mailist_subscribe', MailingListSubscribeFromStatus.as_view(),
         name='status_subscribe'),
    path('mailist_unsubscribe/<int:mailing_list>',
         MailingListUnsubscribeFromStatus.as_view(), name='status_unsubscribe')

]

# For debugging the "thank you" template:
if hasattr(settings, 'ROLE') and 'production' != settings.ROLE:
    urlpatterns.append(path('merci', MailingListMerci.as_view(),
                            name='list_ok'))
    urlpatterns.append(path('inscrire-captcha',
                            QuickMailingListSignup.as_view(),
                            name='quick_list_signup'),)
