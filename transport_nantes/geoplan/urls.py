from django.urls import path
from .views import MapView

app_name = "geoplan"

urlpatterns = [
    path('', MapView.as_view(), name="map")
]
