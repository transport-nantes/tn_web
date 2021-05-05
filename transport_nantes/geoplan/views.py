from django.shortcuts import render
from django.views.generic import TemplateView

from .models import MapPage

import folium
from pathlib import Path
# Create your views here.
class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def __init__(self):
        self.build_map()

    def build_map(self, link=None):
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
