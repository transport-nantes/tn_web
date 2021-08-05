from django.urls import path
from .views import (StripeView)

app_name = "stripe_app"

urlpatterns = [
    path('', StripeView.as_view(), name="stripe"),
]
