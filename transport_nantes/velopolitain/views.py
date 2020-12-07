from django.views.generic.base import TemplateView
from django.urls import reverse

class MainVelopolitain(TemplateView):
    template_name = 'velopolitain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Transport Nantes | Vélopolitain"
        context['hero'] = True
        context['hero_image'] = 'asso_tn/images-quentin-boulegon/vélopolitain-1.jpg'
        context['hero_title'] = 'Le Vélopolitain'
        context['twitter_title'] = "Vélopolitain | Nantes - Un aménagement cyclable continu, lisible et sécurisé."
        context['twitter_description'] = "Le vélopolitain a pour mission d’améliorer et de sécuriser les pistes cyclables sur Nantes métropole."
        context['twitter_image'] = "asso_tn/velopolitain-cest-quoi.jpg"
        return context

class BlogVelopolitain(TemplateView):
    """Should this perhaps move to communications/ ?
    """
    # We should have three types of blogs.
    #
    # 1.  This kind that is template-driven.  Although it doesn't seem
    #     to be possible to set variables in the template that are then
    #     seen in the base template, so we still have to use the map.
    #
    # 2.  The random next blog.  And the hero image is probably by
    #     class overridable individually as desired.
    #
    # 3.  Something database driven, which doesn't exist yet.
    hero_map = {
        'gilets': {'image': 'velopolitain/gilet-banner.png',
                   'title': 'Les rencontres visibles',},
        'intro': {'image': 'asso_tn/images-quentin-boulegon/vélopolitain-1.jpg',
                  'title': 'Le Vélopolitain sur Nantes Métropole',},
        'laboratoire': {'image': 'asso_tn/images-quentin-boulegon/vélopolitain-1.jpg',
                  'title': 'Le Laboratoire du Vélopolitain',},
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = context['slug']
        if slug in self.hero_map:
            context['hero'] = True
            hero_data = self.hero_map[context['slug']]
            context['title'] = "Vélopolitain"
            context['hero_image'] = hero_data['image']
            context['hero_title'] = hero_data['title']
        self.template_name = 'velopolitain/{sl}.html'.format(sl=context['slug'])
        context['twitter_title'] = "Vélopolitain | Nantes - Un aménagement cyclable continu, lisible et sécurisé."
        context['twitter_description'] = "Le vélopolitain a pour mission d’améliorer et de sécuriser les pistes cyclables sur Nantes métropole."
        # Argument passed is the slug.  This should become a db lookup instead.
        # For the moment, all slugs lead to the laboratoire.
        return context
