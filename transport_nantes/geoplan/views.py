from django.http import Http404, HttpResponse
from django.views.generic import TemplateView, View
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max

import folium
from folium import plugins

from .models import MapContent, MapDefinition


# Create your views here.


class MapView(TemplateView):
    template_name = "geoplan/base_map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        city = kwargs["city"]
        observatory_name = kwargs["observatory_name"]
        try:
            map_definition = MapDefinition.objects.get(
                observatory_name=observatory_name, city=city)
        except ObjectDoesNotExist:
            raise Http404(f"{city} ou l'observatoire {observatory_name}\
                n'existe(nt) pas")

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
        # CartoDB is a Black and white map to highlight colors
        folium.TileLayer('cartodb positron', attr="CartoDB").add_to(geomap)
        # CyclOSM displays cyclist oriented information like parking, pathways.
        folium.TileLayer(
            tiles='https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
            attr='<a href="https://github.com/cyclosm/cyclosm-cartocss-style/releases" title="CyclOSM - Open Bicycle render">CyclOSM</a> | Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            name="CyclOSM").add_to(geomap)

        # styles args : https://leafletjs.com/reference-1.6.0.html#path-option
        styles=[{'color': '#000000', "dashArray": "1 10"},
                {'color': '#9BBF85', 'weight': 7}, #006164, #9BBF85
                {'color': '#B3589A', 'weight': 7},]#B3589A , #DB4325


        for map_content in map_content_rows:
            # Adds a layer to the map
            geojson = map_content.geojson
            layer_name = map_content.map_layer.layer_name
            if map_content.map_layer.layer_type == "BASE":
                index = 0
                # Creates a group to hold all sublayers
                # will allow toogle/untoggle
                group = folium.FeatureGroup(name=map_content.map_layer.layer_name)
                geomap.add_child(group)
                folium.GeoJson(geojson, name=layer_name,
                # This lambda function is mandatory to use the
                # style_function argument. It passes a dict as argument
                # which contains datas about the layer (like the coordinates)
                # This dict is stored in the "_" argument, deleting it woult
                # result in the first argument being overridden by the dict.
                # styles is a list of dict containing args to set various
                # styles settings such as thickness, opacity, color...
                style_function=lambda _, ind=index, style=styles: style[ind])\
                .add_to(group)
            elif map_content.map_layer.layer_type == "SATISFAIT":
                index = 1
                # Add a sub group that will be toggled when the
                # main group is toggled. Layers are added to subgroups
                # as long as no new main group is defined.
                subgroup = plugins.FeatureGroupSubGroup(group,
                                        name=map_content.map_layer.layer_name)
                geomap.add_child(subgroup)
                folium.GeoJson(geojson, name=layer_name,
                style_function=lambda _, ind=index, style=styles: style[ind])\
                .add_to(subgroup)
            elif map_content.map_layer.layer_type == "NON SATISFAIT":
                index = 2
                subgroup = plugins.FeatureGroupSubGroup(group,
                                        name=map_content.map_layer.layer_name)
                geomap.add_child(subgroup)
                folium.GeoJson(geojson, name=layer_name,
                style_function=lambda _, ind=index, style=styles: style[ind])\
                .add_to(subgroup)
            else: # Raise 404 if the layer isn't set properly
                raise Http404(f"Il y a un problème avec la couche {map_content.map_layer.layer_name}.\
                            Veuillez contacter l'administreur.")

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
        filename = "MOBILITAINS_" + str(last_layer.map_layer.layer_name).replace(" ", "_") + "_" \
            + str(last_layer.timestamp).replace(":", "-")\
                .replace(" ", "_")[:19] + ".geojson"

        # Allows user to download the GeoJSON file.
        # Name is the same as in database.
        response = HttpResponse(geojson, content_type="application/json")
        response['Content-Disposition'] = "attachment; filename=" + filename

        return response
