from django.urls import path
from . import views

app_name = 'mobilito'

urlpatterns = [
    path('', views.MobilitoView.as_view(), name='index'),
    path('tutoriel/<str:tutorial_page>/', views.TutorialView.as_view(),
         name='tutorial'),
    path('formulaire-adresse', views.AddressFormView.as_view(),
         name='address_form'),

    path('enregistrement/', views.RecordingView.as_view(), name='recording'),
    path('merci/', views.ThankYouView.as_view(), name='thanks'),
    path('session/<str:session_sha1>/', views.SessionSummaryView.as_view(),
         name='session_summary'),

    path('ajax/create-event/', views.create_event, name='event_creation'),
]
