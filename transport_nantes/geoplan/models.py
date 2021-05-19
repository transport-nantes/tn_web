from django.db import models

# Create your models here.

class MapPage(models.Model):

    city = models.CharField(max_length=50)
    observatory_name = models.CharField(max_length=50)
    observatory_type = models.CharField(max_length=50)
    layer_name = models.CharField(max_length=50)
    layer_position = models.IntegerField()
    geojson = models.TextField()
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=False)
    kilometres = models.FloatField()

class MapDefinition(models.Model):
    """Primary model to display maps according to the city name.
    city field will get retrieved to create the url leading to the observatory.
    /observatoire/<city>/<observatory_type>
    """
    # City name : "Nantes"
    city = models.CharField(max_length=50)
    # Public display of what we're looking at : "Plan vélo théorique voté en Juin 2020"
    observatory_name = models.CharField(max_length=50)
    # Sort of observatory, in prevision of future other maps (public transports, bike...)
    observatory_type = models.SlugField(max_length=100)

    # Longitude and latitude of the city according to OpenStreetMap
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self):
        return '{city} / {observatory_name}'.format(city=self.city,
        observatory_name=self.observatory_name)


class MapLayer(models.Model):
    """Will set parameters for different layers caintained in the MapDefinition"""
    map_definition = models.ForeignKey(MapDefinition, on_delete=models.CASCADE)
    layer_name = models.CharField(max_length=100)

    # Depth = position on the stack
    layer_depth = models.SmallIntegerField()

    def __str__(self):
        return self.layer_name


class MapContent(models.Model):
    """Actual content of the layer, displayed on the map"""
    map_layer = models.ForeignKey(MapLayer, on_delete=models.CASCADE)

    # Raw  geojson file
    geojson = models.TextField()

    # Timestamp at creation date, not on edit (we're saving a history)
    timestamp = models.DateTimeField(auto_now_add=True)