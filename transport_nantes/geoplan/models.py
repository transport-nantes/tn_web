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