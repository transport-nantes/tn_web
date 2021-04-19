from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class ButtonsView(TemplateView):
    template_name = "buttons.html"