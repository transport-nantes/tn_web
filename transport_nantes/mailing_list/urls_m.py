from django.urls import path
from django.conf import settings
from .views_m import *
# from asso_tn.views import AssoView
from .forms import QuickPetitionSignupForm

app_name = 'mailing_list'
urlpatterns = [
    path('inscrire', MailingListSignupM.as_view(), name='list_signup'),
    path('inscrire-captcha', QuickMailingListSignupM.as_view(), name='quick_list_signup'),

    path('petition-captcha', QuickPetitionSignup.as_view(), name='quick_petition_signup'),
    path('petition/<slug:petition_slug>/', PetitionView.as_view(
        template_name='mailing_list/petition4.html'),
         name='petition'),
]

# For debugging the thankyou template:
if hasattr(settings, 'ROLE') and 'production' != settings.ROLE:
    urlpatterns.append(path('merci', MailingListMerciM.as_view(), name='list_ok'))
