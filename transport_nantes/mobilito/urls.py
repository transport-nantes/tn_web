from django.urls import path
from . import views

app_name = 'mobilito'

urlpatterns = [
    path('', views.MobilitoView.as_view(), name='index'),
    path('tutoriel/', views.TutorialView.as_view(), name='tutorial'),

    path('enregistrement/', views.RecordingView.as_view(), name='recording'),
    path('merci/', views.ThankYouView.as_view(), name='thanks'),

    path('ajax/create-event/', views.create_event, name='event_creation'),
]
