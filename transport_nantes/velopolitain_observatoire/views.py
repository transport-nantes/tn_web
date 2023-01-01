from django.views.generic.base import TemplateView

# Create your views here.


class MainVelopolitainObservatoire(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = "velopolitain_observatoire/{sl}.html".format(
            sl=context["slug"]
        )
        return context


class VelopolitainObservatoireCountApp(TemplateView):
    template_name = "velopolitain_observatoire/count_app.html"


class VelopolitainObservatoireCountForm(TemplateView):
    template_name = "velopolitain_observatoire/count_form.html"
