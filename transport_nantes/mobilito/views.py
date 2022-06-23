from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView


class MobilitoView(TemplateView):
    template_name = 'mobilito/index.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('mobilito:tutorial'))
        return super().get(request, *args, **kwargs)


class TutorialView(TemplateView):
    template_name = 'mobilito/tutorial.html'
