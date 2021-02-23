from django.views.generic.base import TemplateView

# Create your views here.

class DashboardIndex(TemplateView):
    """Present dashboard index.

    I haven't finished designing this, so it's anybody's guess what I
    mean here.  I need to see something rough to figure out what I
    want.

    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = 'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg'
        context['hero_title'] = 'dashboard'
        context['hero_description'] = '(machin)'
        return context

