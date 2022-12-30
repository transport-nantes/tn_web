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
    path("mes-sessions/", views.MySessionHistoryView.as_view(), name='my_sessions'),
    path('session/<str:session_sha1>/', views.MobilitoSessionSummaryView.as_view(),
         name='mobilito_session_summary'),
    path('update-location/<str:session_sha1>/', views.EditLocationView.as_view(),
         name='edit_location'),

    path('session_ts_img/<str:session_sha1>/', views.mobilito_session_timeseries_image,
         name='mobilito_session_timeseries_image'),
    path('session_frac_img/<str:session_sha1>/', views.mobilito_session_fraction_image,
         name='mobilito_session_fraction_image'),

    path('ajax/create-event/', views.create_event, name='event_creation'),
    path('ajax/get-address/', views.ReverseGeocodingView.as_view(),
         name='geocoding'),
    path('ajax/report-session/<str:session_sha1>/', views.flag_session,
         name='flag_session'),
]
