from django.urls import path

from . import views_m

# We generally call these "questionnaire" now, but originally we
# called them "survey", at least in English.

app_name = 'surveys'
urlpatterns = [
    path('', views_m.MainSurveyView.as_view(), name='survey_root'),
    path('questions/<slug:slug>',
         views_m.QuestionnaireView.as_view(),
         name='questions'),
    path('commune/<int:survey_id>',
         views_m.CommuneChooserSurveyView.as_view(),
         name='choose_commune'),
    path('liste/<int:survey_id>/<int:commune_id>',
         views_m.ListeChooserSurveyView.as_view(),
         name='choose_liste'),
    path('question/<int:survey_id>/<int:commune_id>/<int:responder_id>',
         views_m.QuestionChooserSurveyView.as_view(),
         name='choose_question'),
    path('response/<int:survey_id>/<int:commune_id>/<int:responder_id>/<int:question_id>',
         views_m.ResponseDisplaySurveyView.as_view(),
         name='choose_response'),
    ## Deprecated, was fixed for 
    # path('questionnaire/<int:survey_id>',
    #      views.QuestionnaireForSurveyView.as_view(),
    #      name='questionnaire'),
]
