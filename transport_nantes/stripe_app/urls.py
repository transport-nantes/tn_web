from django.urls import path
from .views import (
    StripeView, get_public_key, create_checkout_session, stripe_webhook)

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
    path('config/', get_public_key),
    path('create-checkout-session/', create_checkout_session ),
    path('success/', StripeView.as_view(
        template_name="stripe_app/success.html")),
    path('cancelled/', StripeView.as_view(
        template_name="stripe_app/cancel.html")),
    path('webhook/', stripe_webhook),
]
