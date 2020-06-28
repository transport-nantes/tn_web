from django.urls import path

from . import views

app_name = 'observatoire'
urlpatterns = [
    path('<int:observatoire_id>',
         views.MainObservatoire.as_view(), name='index'),
]
