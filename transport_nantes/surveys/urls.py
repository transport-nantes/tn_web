from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:survey_id>/commune/', views.choose_commune, name='liste'),
    path('<int:survey_id>/<int:commune_id>/liste', views.choose_liste, name='liste'),
    path('<int:survey_id>/<int:commune_id>/<int:responder_id>/question',
         views.choose_question, name='question'),
    path('<int:survey_id>/<int:commune_id>/<int:responder_id>/<int:question_id>/response',
         views.choose_response, name='response'),
]
