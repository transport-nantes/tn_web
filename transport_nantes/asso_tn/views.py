from django.views.generic.base import TemplateView

# Create your views here.
class MainTransportNantes(TemplateView):
    template_name = 'asso_tn/index.html'
    twitter_image = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = "asso_tn/images-quentin-boulegon/pont-rousseau-1.jpg"
        context['hero_title'] = "Pour une mobilité sûre, vertueuse, et agréable"
        context['title'] = "Mobilitains - Pour une mobilité multimodale"
        context['twitter_image'] = "asso_tn/accueil-mobilité-multimodale.jpg"
        return context

class AssoView(TemplateView):
    title = None
    hero_image = None
    hero_title = None
    hero_description = None
    meta_descr = ""
    twitter_title = ""
    twitter_descr = ""
    twitter_image = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        social = {}
        social["twitter_title"] = self.twitter_title
        social["twitter_description"] = self.twitter_descr
        social["twitter_image"] = self.hero_image
        social["og_image"] = self.hero_image
        page = {}
        page["meta_descr"] = self.meta_descr
        context['title'] = self.title
        context["page"] = page
        context["social"] = social
        if self.hero_image is not None:
            context['hero'] = True
            context['hero_image'] = self.hero_image
            context['hero_title'] = self.hero_title or ""
            context['hero_description'] = self.hero_description or ""
            context["is_static"] = True
        return context
