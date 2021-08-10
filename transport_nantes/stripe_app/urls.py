from django.urls import path
from .views import (StripeView, get_public_key, create_checkout_session)

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
    path('config/', get_public_key),
    path('create-checkout-session/', create_checkout_session,
         name="checkout-session"),
]
