from django.views.generic.base import TemplateView
# from django.shortcuts import render
from .models import Observatoire

class MainObservatoire(TemplateView):
    template_name = 'observatoire/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(kwargs)
        context['observatoire'] = Observatoire.objects.filter(
            id=kwargs['observatoire_id'])[0]
        print(context['observatoire'])
        return context
