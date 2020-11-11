from django.views.generic.base import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site

# Create your views here.
class MainTransportNantes(TemplateView):
    template_name = 'asso_tn/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = "asso_tn/images-quentin-boulegon/pont-rousseau-1.jpg"
        # print(dir(context['view'].request))
        # print(get_current_site(context['view'].request))
        # print(Site.objects.get_current().domain == 'example.com')
        return context

class AssoView(TemplateView):
    hero_image = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.hero_image is not None:
            context['hero'] = True
            context['hero_image'] = self.hero_image
        return context
