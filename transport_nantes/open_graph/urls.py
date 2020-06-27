from django.urls import path

from . import views

app_name = 'open_graph'
urlpatterns = [
    path('', views.generate_questionnaire_image, name='index'),
]
