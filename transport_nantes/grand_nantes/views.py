from django.views.generic.base import TemplateView

# Create your views here.
class MainGrandNantes(TemplateView):
    template_name = 'grand_nantes/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        # context['hero_image'] = '/static/asso_tn/images-libres/grande-mobilité-1000.jpg'
        context['hero_image'] = '/static/asso_tn/images-quentin-boulegon/grande-mobilité-1.jpg'
        return context
