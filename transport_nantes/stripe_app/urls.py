from django.urls import path
from .views import (StripeView, get_public_key)

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
    path('config/', get_public_key),
]
