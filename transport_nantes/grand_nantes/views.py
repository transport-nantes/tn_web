from django.views.generic.base import TemplateView

# Create your views here.
class MainGrandNantes(TemplateView):
    template_name = 'grand_nantes/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
