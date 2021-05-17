from datetime import datetime
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist


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
            "timestamp": datetime.now()
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
        response = self.client.get("/observatoire/testcity/planvelo/NOTtestlayer")
        self.assertRaises(ObjectDoesNotExist)

        # 200 if the layer exists.
        response = self.client.get("/observatoire/testcity/planvelo/testlayer")
        self.assertEqual(response.status_code, 200)
