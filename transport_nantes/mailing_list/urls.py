from django.urls import path
from .views import (
    MailingListSignup,
    NewsletterUnsubscriptionView,
    PressSubscriptionManagementView,
    QuickPetitionSignup,
    PetitionView,
    MailingListListView,
    QuickMailingListSignup,
    UserStatusView,
    MailingListToggleSubscription,
)

app_name = "mailing_list"
urlpatterns = [
    path("inscrire", MailingListSignup.as_view(), name="list_signup"),
    path(
        "newsletters-signup",
        QuickMailingListSignup.as_view(),
        name="quick_signup",
    ),
    path(
        "petition-captcha",
        QuickPetitionSignup.as_view(),
        name="quick_petition_signup",
    ),
    path(
        "petition/<slug:petition_slug>/",
        PetitionView.as_view(template_name="mailing_list/petition4.html"),
        name="petition",
    ),
    path("list", MailingListListView.as_view(), name="list_items"),
    path("status", UserStatusView.as_view(), name="user_status"),
    path(
        "toggle_subscription",
        MailingListToggleSubscription.as_view(),
        name="toggle_subscription",
    ),
    path(
        "unsub/newsletter/<str:token>",
        NewsletterUnsubscriptionView.as_view(),
        name="newsletter_unsubscribe",
    ),
    path(
        "manage/press/<str:token>",
        PressSubscriptionManagementView.as_view(),
        name="press_subscription_management",
    ),
]
