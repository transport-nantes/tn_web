from django.http import Http404, HttpResponse
from django.views.generic import TemplateView, View
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

import folium

from .models import MapContent, MapDefinition


# Create your views here.


class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = kwargs["city"]
        observatory_name = kwargs["observatory_name"]
        map_definition = MapDefinition.objects.filter(
            city=city,
            observatory_name=observatory_name)

        # Gets all layers corresponding to a city and its observatory
        map_content_rows = MapContent.objects.filter(
            map_layer__map_definition__city=city,
            map_layer__map_definition__observatory_name=observatory_name)\
                .order_by("map_layer__layer_depth")

        # Gets a dict of all unique layers with their latest timestamp
        unique_layers = map_content_rows.values("map_layer__layer_name")\
            .annotate(latest=Max("timestamp"))

        # Makes a query containing the latest version of layers
        combined_queries = MapContent.objects.none()
        for item in unique_layers:
            combined_queries = combined_queries | \
            MapContent.objects.filter(timestamp=item["latest"])

        map_content_rows = combined_queries.order_by("map_layer__layer_depth")
        # Checks if the query isn't empty,
        # otherwise it would use unbound values.
        if map_content_rows.__len__() == 0:
            raise Http404("Page non trouvée (404)")

        # Building the map
        lat = map_content_rows[0].map_layer.map_definition.latitude
        lon = map_content_rows[0].map_layer.map_definition.longitude
        geomap = folium.Map(location=[lat, lon], zoom_start=12)

        for map_content in map_content_rows:
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
        context["map_defn"] = map_definition

        # Produces a tuple (url-compatible layer name, layer name) for
        # each layer in the map.
        context["layers_url"] = [map_content_rows[i].map_layer.layer_name
            for i in range(len(map_content_rows))]

        # Hack, hard code for today.
        context['social'] = {}
        context['social']['og_title'] = "L'Observatoire du Vélopolitain"
        context['social']['og_description'] = "Suivez l'avancement du vélo à Nantes Métropole"
        context['social']['og_image'] = "asso_tn/20210228-210131-9011_velorution-psm-sm.jpg"
        context['social']['twitter_title'] = context['social']['og_title']
        context['social']['twitter_description'] = context['social']['og_description']
        context['social']['twitter_image'] = context['social']['og_image']

        return context

class DownloadGeoJSONView(View):

    def get(self, request, **kwargs):

        # Retrieved from URL
        city = kwargs["city"]
        observatory_name = kwargs["observatory_name"]
        layer_name = kwargs["layer_name"]


        try:
        # Gets latest layer on a given city/observatory/layer set.
            last_layer = MapContent.objects.filter(
                map_layer__map_definition__city=city,
                map_layer__map_definition__observatory_name=observatory_name,
                map_layer__layer_name=layer_name).order_by(
                    'map_layer__layer_depth').latest('timestamp')
        except ObjectDoesNotExist:
            raise Http404(f"La couche {layer_name} \
                n'existe pas pour l'observatoire {observatory_name} à {city}")

        geojson = last_layer.geojson

        # File name
        filename = "MOBILITAINS_" + last_layer.map_layer.layer_name + "_" \
            + str(last_layer.timestamp).replace(":", "-")\
                .replace(" ", "_")[:19] + ".geojson"

        # Allows user to download the GeoJSON file.
        # Name is the same as in database.
        response = HttpResponse(geojson, content_type="application/json")
        response['Content-Disposition'] = "attachment; filename=" + filename

        return response
