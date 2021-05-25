from django.urls import path
from .views import StripeView, CheckoutSession

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
    path('create-checkout-session/', CheckoutSession.as_view(),
        name="checkout_session")
]
