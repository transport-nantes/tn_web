from django.urls import path
from .views import (
    StripeView, SuccessView, get_public_key, create_checkout_session,
    stripe_webhook, tracking_progression)

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
    path('config/', get_public_key),
    path('create-checkout-session/', create_checkout_session,
         name="checkout-session"),
    path('success/', SuccessView.as_view(), name="stripe_success"),
    path('cancelled/', StripeView.as_view(
        template_name="stripe_app/cancel.html")),
    path('webhook/', stripe_webhook),
    path('tracking/', tracking_progression)
]
