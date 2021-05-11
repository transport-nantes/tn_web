from django.http import Http404
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
        city = kwargs["city"]
        observatory_name = kwargs["observatory_name"]

        try:
            map_content = MapContent.objects.get(
                map_layer__map_definition__city=city, map_layer__map_definition__observatory_name=observatory_name)
        except:
                raise Http404("Page non trouvée (404)")
        
        geojson = map_content.geojson
        layer_name = map_content.map_layer.layer_name
        lat, lon = map_content.map_layer.map_definition.latitude, map_content.map_layer.map_definition.longitude

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