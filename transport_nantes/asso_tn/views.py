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
    title = None
    hero_image = None
    hero_title = None
    hero_description = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context['view'].request.GET.get('dog'))
        print(context['view'].request.GET.keys())
        context['title'] = self.title
        if self.hero_image is not None:
            context['hero'] = True
            context['hero_image'] = self.hero_image
            context['hero_title'] = self.hero_title or ""
            context['hero_description'] = self.hero_description or ""
        return context
