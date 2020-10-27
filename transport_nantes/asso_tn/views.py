from django.views.generic.base import TemplateView
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site

# Create your views here.
class MainTransportNantes(TemplateView):
    template_name = 'asso_tn/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = "/static/asso_tn/images-quentin-boulegon/pont-rousseau-1.jpg"
        # print(dir(context['view'].request))
        # print(get_current_site(context['view'].request))
        # print(Site.objects.get_current().domain == 'example.com')
        return context

class AssoView(TemplateView):
    hero_image_map = {'asso_tn/qui-sommes-nous.html':
                      "/static/asso_tn/happy-folks-1000.jpg", # 
                      'asso_tn/join.html':
                      "/static/asso_tn/happy-folks-1000.jpg", # 
                      'asso_tn/contact.html':
                      "/static/asso_tn/happy-folks-1000.jpg", #
                      'asso_tn/ambassadeur.html':
                      "/static/asso_tn/happy-folks-1000.jpg", #
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.template_name in self.hero_image_map:
            context['hero'] = True
            context['hero_image'] = self.hero_image_map[self.template_name]
        return context
