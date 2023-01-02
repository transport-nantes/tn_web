from django.urls import path, register_converter

from . import views


class NegativeIntConverter:
    regex = "-?\\d+"

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return "%d" % value


register_converter(NegativeIntConverter, "negint")

app_name = "open_graph"
urlpatterns = [
    path("pm", views.generate_questionnaire_image, name="parlons-mobilite"),
    path(
        "100j/<str:nonce>/<negint:day_offset>/<negint:edile>",
        views.generate_100_days_image,
        name="100jours",
    ),
]
