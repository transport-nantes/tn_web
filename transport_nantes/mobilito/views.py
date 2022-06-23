from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView


class MobilitoView(TemplateView):
    """Present Mobilito landing page.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/index.html'


class TutorialView(TemplateView):
    """Present the tutorial.

    This is far too simple, but it will stand in for the moment.
    """

    template_name = 'mobilito/tutorial.html'
