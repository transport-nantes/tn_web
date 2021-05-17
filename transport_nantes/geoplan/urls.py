from django.urls import path
from .views import MapView, DownloadGeoJSONView

app_name = "geoplan"

urlpatterns = [
    # This URL is being parsed, city must be an existing city name in database,
    # and observatory name the one indicated in the city object.
    path('<city>/<observatory_name>', MapView.as_view(), name="map"),
    path('<city>/<observatory_name>/<layer_name>', DownloadGeoJSONView.as_view(), name="map")
]
