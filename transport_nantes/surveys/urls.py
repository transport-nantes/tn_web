from django.urls import path

from . import views

# We generally call these "questionnaire" now, but originally we
# called them "survey", at least in English.

app_name = 'surveys'
urlpatterns = [
    path('', views.MainSurveyView.as_view(), name='survey_root'),
    path('questions/<slug:slug>',
         views.QuestionnaireView.as_view(),
         name='questions'),

    # For answering questions.
    path('repondre/1/<slug:slug>',
         views.ResponseView.as_view(),
         name='response_1'),

    # For viewing results.
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
    ## Deprecated, was fixed for 
    # path('questionnaire/<int:survey_id>',
    #      views.QuestionnaireForSurveyView.as_view(),
    #      name='questionnaire'),
]
