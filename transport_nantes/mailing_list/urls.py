from django.urls import path
from django.conf import settings
from .views import (MailingListSignup, QuickMailingListSignup,
                    QuickPetitionSignup, PetitionView, MailingListMerci,
                    DashboardView, FirstStepQuickMailingListSignup)

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

    path('dashboard', DashboardView.as_view(), name='dashboard')
]

# For debugging the "thank you" template:
if hasattr(settings, 'ROLE') and 'production' != settings.ROLE:
    urlpatterns.append(path('merci', MailingListMerci.as_view(),
                            name='list_ok'))
    urlpatterns.append(path('inscrire-captcha',
                            QuickMailingListSignup.as_view(),
                            name='quick_list_signup'),)
