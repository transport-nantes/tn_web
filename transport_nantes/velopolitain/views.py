from django.views.generic.base import TemplateView
from django.urls import reverse

class MainVelopolitain(TemplateView):
    template_name = 'velopolitain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BlogVelopolitain(TemplateView):
    """Should this perhaps move to communications/ ?
    """
    hero_image_map = {
        'gilets': '/static/velopolitain/gilet-banner.png', #
        'intro': '/static/asso_tn/images-quentin-boulegon/vélopolitain-1.jpg', # 
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['slug'] in self.hero_image_map:
            context['hero'] = True
            context['hero_image'] = self.hero_image_map[context['slug']]
        self.template_name = 'velopolitain/{sl}.html'.format(sl=context['slug'])
        # Argument passed is the slug.  This should become a db lookup instead.
        # For the moment, all slugs lead to the laboratoire.
        return context
