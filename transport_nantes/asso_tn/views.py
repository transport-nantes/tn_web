from django.views.generic.base import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site

# Create your views here.
class MainTransportNantes(TemplateView):
    template_name = 'asso_tn/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(dir(context['view'].request))
        print(get_current_site(context['view'].request))
        print(Site.objects.get_current().domain == 'example.com')
        return context
