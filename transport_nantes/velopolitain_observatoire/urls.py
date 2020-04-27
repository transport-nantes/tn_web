from django.urls import path

from . import views

app_name = 'velopolitain_observatoire'
urlpatterns = [
    path('', views.MainVelopolitainObservatoire.as_view(), name='vobs_index'),
]
