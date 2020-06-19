from django.urls import path

from . import views

app_name = 'velopolitain_observatoire'
urlpatterns = [
    path('', views.MainVelopolitainObservatoire.as_view(), name='vobs_index'),
    path('b/<str:slug>', views.MainVelopolitainObservatoire.as_view(), name='blog'),
    path('observatoire', views.VelopolitainObservatoireCountApp.as_view(), name='count_app'),
    path('rattrapage', views.VelopolitainObservatoireCountForm.as_view(), name='count_form'),
]
