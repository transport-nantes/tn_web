from django.views.generic.base import TemplateView

# Create your views here.
class MainVelopolitain(TemplateView):
    template_name = 'velopolitain/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BlogVelopolitain(TemplateView):
    template_name = 'velopolitain/blog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Argument passed is the slug.  This should become a db lookup instead.
        # For the moment, all slugs lead to the laboratoire.
        return context
