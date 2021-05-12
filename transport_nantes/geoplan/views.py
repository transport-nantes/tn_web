from django.http import Http404
from django.views.generic import TemplateView

import folium

from .models import MapContent


# Create your views here.


class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = kwargs["city"]
        observatory_name = kwargs["observatory_name"]

        # Gets all layers corresponding to a city and its observatory
        map_content_rows = MapContent.objects.filter(
            map_layer__map_definition__city=city,
            map_layer__map_definition__observatory_name=observatory_name).order_by(
                "map_layer__layer_depth")

        # Checks if the query isn't empty, otherwise it would use unbound values.
        if map_content_rows.__len__() == 0:
            raise Http404("Page non trouvée (404)")

        for index, map_content in enumerate(map_content_rows):
            if index == 0:
                # Building the map
                lat = map_content.map_layer.map_definition.latitude
                lon = map_content.map_layer.map_definition.longitude
                geomap = folium.Map(location=[lat, lon], zoom_start=12)

            # Adds a layer to the map
            geojson = map_content.geojson
            layer_name = map_content.map_layer.layer_name
            folium.GeoJson(geojson, name=layer_name).add_to(geomap)

        # This is the Layer filter to enable / disable datas on map
        folium.LayerControl(hideSingleBase=True).add_to(geomap)

        # Produce html code to embed on our page
        root = geomap.get_root()
        html = root.render()
        context["html_map"] = html

        return context
