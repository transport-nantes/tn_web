from django.views.generic.base import TemplateView

# Create your views here.
class MainTransportNantes(TemplateView):
    template_name = 'asso_tn/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
