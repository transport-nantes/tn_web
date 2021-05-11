from django.urls import path
from .views import MapView

app_name = "geoplan"

urlpatterns = [
    path('<city>/<observatory_name>', MapView.as_view(), name="map")
]
