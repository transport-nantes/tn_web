from django.views.generic.base import TemplateView

# Create your views here.
class MainVelopolitain(TemplateView):
    template_name = 'velopolitain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
