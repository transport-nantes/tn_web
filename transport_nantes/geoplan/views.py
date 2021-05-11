from django.shortcuts import render
from django.views.generic import TemplateView
import requests

from .models import MapPage, MapDefinition, MapLayer, MapContent

import folium
from pathlib import Path
# Create your views here.
class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Will need to retrieve that from browser probably
        context["city"] = "Nantes"

        # The __iexact part makes the search not case senstive (Nantes = nantes)
        city = MapDefinition.objects.get(city__iexact=context["city"])
        layer = MapLayer.objects.get(map_definition=city)
        content = MapContent.objects.get(map_layer=layer)

        # Variables used by folium
        geojson = content.geojson
        lat, lon = city.latitude, city.longitude
        layer_name = layer.layer_name

        # Building the map
        m = folium.Map(location=[lat, lon], zoom_start=12)
        # It only loads one geojson file as a layer for now
        folium.GeoJson(geojson, name=layer_name).add_to(m)
        # This is the Layer filter to enable / disable datas on map
        folium.LayerControl(hideSingleBase=True).add_to(m)

        # Produce html code to embed on our page
        root = m.get_root()
        html = root.render()
        context["html_map"] = html

        return context
