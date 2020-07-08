from django.views.generic.base import TemplateView
# from django.shortcuts import render
from .models import Observatoire, ObservatoirePerson, ObservatoireObjective
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

class ProgressObservatoire(TemplateView):
    template_name = 'observatoire/progress.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(kwargs)
        observatoire = Observatoire.objects.filter(
            id=kwargs['observatoire_id'])[0]
        context['day_offset'] = (datetime.date.today() - observatoire.start_date).days
        context['observatoire'] = observatoire
        if 'person_id' in kwargs:
            context['edile'] = kwargs['person_id']
            this_person = ObservatoirePerson.objects.filter(
                id=kwargs['person_id'])[0]
            context['this_person'] = this_person
            context['objectives'] = ObservatoireObjective.objects.filter(
                person=this_person)
        else:
            context['edile'] = ''
        persons = ObservatoirePerson.objects.filter(
            observatoire_id=kwargs['observatoire_id']).order_by('entity')
        context['persons'] = persons
        print(context)
        print(type(context['day_offset']))
        return context

class BlogObservatoire(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = 'observatoire/{sl}.html'.format(sl=context['slug'])
        observatoire = Observatoire.objects.filter(
            id=kwargs['observatoire_id'])[0]
        context['observatoire'] = observatoire
        context['day_offset'] = (datetime.date.today() - observatoire.start_date).days
        return context
