from django.views.generic.base import TemplateView
# from django.shortcuts import render
from .models import Observatoire
import datetime

class MainObservatoire(TemplateView):
    template_name = 'observatoire/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(kwargs)
        observatoire = Observatoire.objects.filter(
            id=kwargs['observatoire_id'])[0]
        context['observatoire'] = observatoire
        context['day_offset'] = (datetime.date.today() - observatoire.start_date).days
        print(context)
        print(type(context['day_offset']))
        return context
