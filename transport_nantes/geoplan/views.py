from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class MapView(TemplateView):
    template_name = "geoplan/map.html"