from django.urls import path, register_converter

from . import views

class NegativeIntConverter:
    regex = '-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value

register_converter(NegativeIntConverter, 'negint')

app_name = 'open_graph'
urlpatterns = [
    path('pm', views.generate_questionnaire_image, name='parlons-mobilite'),
    path('survey/c/<int:commune_id>', views.generate_election_commune_image, name='survey-commune'),
    path('survey/cc/<int:candidate_id>',
         views.generate_election_candidate_image, name='survey-candidate'),
    path('survey/ccq/<int:candidate_id>/<int:question_id>',
         views.generate_election_question_image, name='survey-question'),
]
