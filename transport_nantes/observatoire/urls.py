from django.urls import path

from . import views

app_name = 'observatoire'
urlpatterns = [
    path('<int:observatoire_id>',
         views.MainObservatoire.as_view(), name='index'),
    path('progress/<int:observatoire_id>',
         views.ProgressObservatoire.as_view(), name='progress'),
    path('progress/<int:observatoire_id>/<int:person_id>',
         views.ProgressObservatoire.as_view(), name='progress'),
    path('b/<int:observatoire_id>/<str:slug>',
         views.BlogObservatoire.as_view(), name='blog'),
]
