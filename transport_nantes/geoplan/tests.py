from copy import deepcopy

from django.test import TestCase
from django.utils.timezone import now
from django.db.models import Max

from .models import MapContent, MapLayer, MapDefinition

# Create your tests here.
class GeoplanTest(TestCase):

    def setUp(self):
        self.definition = {
            "city":"testcity",
            "observatory_name" :"planvelo",
            "observatory_type": "test",
            "longitude": 0.00,
            "latitude": 0.00
            }

        # Assignement because an instance is required in Foreign keys
        map_def = MapDefinition.objects.create(**self.definition)

        self.layer = {
            "map_definition" : map_def,
             "layer_name":"testlayer",
             "layer_depth" : 0
        }

        map_lay = MapLayer.objects.create(**self.layer)

        self.content = {
            "map_layer": map_lay,
            "geojson": """{
                "type": "FeatureCollection",
                "name": "reseau_velo_metropolitain_4326",
                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                "features": [
                    {"type": "Feature", "properties": {"id": 1}, "geometry": {
                        "type": "MultiLineString", "coordinates": [[ -1.710792615591268, 47.210384214678122 ]]}}
                ]
            }""",
            "timestamp": now()
        }

        self.timestamp_1 = deepcopy(self.content["timestamp"])
        MapContent.objects.create(**self.content)

        # Creating an updated testlayer for testcity
        self.layer = {
            "map_definition" : map_def,
             "layer_name":"testlayer",
             "layer_depth" : 0
        }

        map_lay = MapLayer.objects.create(**self.layer)

        self.content = {
            "map_layer": map_lay,
            "geojson": """{
                "type": "FeatureCollection",
                "name": "reseau_velo_metropolitain_4326",
                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                "features": [
                    {"type": "Feature", "properties": {"id": 1}, "geometry": {
                        "type": "MultiLineString", "coordinates": [[ -2, 47 ]]}}
                ]
            }""",
            # This timestamp will be after the first layer
            "timestamp": now()
        }

        MapContent.objects.create(**self.content)

        # Creates a 2nd layer for testcity

        self.layer = {
            "map_definition" : map_def,
             "layer_name":"testlayer2",
             "layer_depth" : 1
        }

        map_lay = MapLayer.objects.create(**self.layer)

        self.content = {
            "map_layer": map_lay,
            "geojson": """{
                "type": "FeatureCollection",
                "name": "reseau_velo_metropolitain_4326",
                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                "features": [
                    {"type": "Feature", "properties": {"id": 1}, "geometry": {
                        "type": "MultiLineString", "coordinates": [[ -2, 47 ]]}}
                ]
            }""",
            "timestamp": now()
        }

        MapContent.objects.create(**self.content)



    def test_observatoire_status_code(self):
        # Proper URL scheme
        response = self.client.get("/observatoire/testcity/planvelo")
        self.assertEqual(response.status_code, 200)

        # Mistake in URL scheme (city name doesn't exist)
        response = self.client.get("/observatoire/NOTtestcity/planvelo")
        self.assertEqual(response.status_code, 404)

        # Mistake in URL scheme (observatory doesn't exit)
        response = self.client.get("/observatoire/testcity/NOTplanvelo")
        self.assertEqual(response.status_code, 404)

    def test_observatoire_layer_download_status_code(self):
        # 404 if layer doesn't exist
        response = self.client.get(
            "/observatoire/testcity/planvelo/NOTtestlayer")
        self.assertEqual(response.status_code, 404)

        # 200 if the layer exists.
        response = self.client.get("/observatoire/testcity/planvelo/testlayer")
        self.assertEqual(response.status_code, 200)

    def test_latest_layer(self):
        latest_layer = MapContent.objects.filter(
            map_layer__map_definition__city="testcity",
            map_layer__map_definition__observatory_name="planvelo",
            map_layer__layer_name="testlayer").latest('timestamp')

        self.assertTrue(latest_layer.timestamp > self.timestamp_1,
            msg=f'layer ={latest_layer.timestamp} t1 = {self.timestamp_1}')

    def test_number_of_layer(self):
        layer_number =MapContent.objects.filter(
            map_layer__map_definition__city="testcity",
            map_layer__map_definition__observatory_name="planvelo").order_by(
                "map_layer__layer_depth")

        unique_layers = layer_number.values_list(
            'map_layer__layer_name', flat=True).distinct()

        latest_layer = layer_number.values("map_layer__layer_name")\
            .annotate(latest=Max("timestamp"))

        combined_queries = MapContent.objects.none()
        for item in latest_layer:
            combined_queries = combined_queries | \
            MapContent.objects.filter(timestamp=item["latest"])

        self.assertTrue(len(combined_queries) == len(unique_layers),
            msg=f"\nlen of filter : {len(layer_number)}\n \
                layer content : {layer_number}\n \
                unique_layers : {unique_layers}\n \
                latest_layers : {latest_layer}\n \
                filter : {len(combined_queries)}")
