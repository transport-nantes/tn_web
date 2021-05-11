from django.shortcuts import render
from django.views.generic import TemplateView
import requests

from .models import MapPage, MapDefinition, MapLayer, MapContent

import folium
from pathlib import Path
# Create your views here.
class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def __init__(self):
        self.build_map()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Will need to retrieve that from browser probably
        context["city"] = "Nantes"
        return context

    def build_map_old(self, link=None):
        """
        Build a map centered on Nantes and adds a layer on it from either local file or link
        """

        if link is not None:
            geojson = str(link)
        else:
            plan_nantes = MapPage.objects.get(city='Nantes')
            field = MapPage._meta.get_field('geojson')
            geojson = field.value_from_object(plan_nantes)


        m = folium.Map(location=[47.2184, -1.5556], zoom_start=12) # Centered on Nantes, can change the map style with the tiles argument
        folium.GeoJson(geojson, name="Plan vélo théorie").add_to(m) # Adding the first layer of the map with the GeoJSON file

        folium.LayerControl(hideSingleBase=True).add_to(m) # Adds the option to filter Layers
        
        template_folder = str(Path(__file__).resolve().parent / 'templates' / 'geoplan')
        m.save(f"{template_folder}/map.html")

    def build_map(self):
        context = self.get_context_data()

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
        context["html_map"] = html.encode('utf8')

        return context