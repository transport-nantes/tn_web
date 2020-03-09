from django.urls import path

from . import views

app_name = 'surveys'
urlpatterns = [
    path('', views.MainSurveyView.as_view(), name='survey_root'),
    path('commune/<int:survey_id>',
         views.CommuneChooserSurveyView.as_view(),
         name='choose_commune'),
    path('liste/<int:survey_id>/<int:commune_id>',
         views.ListeChooserSurveyView.as_view(),
         name='choose_liste'),
    path('question/<int:survey_id>/<int:commune_id>/<int:responder_id>',
         views.QuestionChooserSurveyView.as_view(),
         name='choose_question'),
    path('response/<int:survey_id>/<int:commune_id>/<int:responder_id>/<int:question_id>',
         views.ResponseDisplaySurveyView.as_view(),
         name='choose_response'),
]
