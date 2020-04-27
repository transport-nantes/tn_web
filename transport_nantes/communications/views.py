from django.views.generic.base import TemplateView

class MainCommunications(TemplateView):
    template_name = 'communications/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class BlogCommunications(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = 'communications/{sl}.html'.format(sl=context['slug'])
        # Argument passed is the slug.  This should become a db lookup instead.
        return context
