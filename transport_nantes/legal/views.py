from django.views.generic.base import TemplateView

# Create your views here.

class MentionsLegalesView(TemplateView):
    template_name = 'legal/mentions_legales.html'
    print('I am MLV!')

    def get_context_data(self, **kwargs):
        print('I am GCD!')
        context = super().get_context_data(**kwargs)
        return context
