from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class ButtonsView(TemplateView):
    template_name = "buttons.html"
    button_dict = {
        "A": {
            "clicks": 0,
            "timestamps": []
            }, 
        "B": {
            "clicks": 0, 
            "timestamps": []
            },
        "C": {
            "clicks": 0, 
            "timestamps": []
            },
        "D": {
            "clicks": 0, 
            "timestamps": []
            },
        }
