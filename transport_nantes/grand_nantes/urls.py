from django.urls import path

from . import views

app_name = 'grand_nantes'
urlpatterns = [
    path('', views.MainGrandNantes.as_view(), name='index'),
]
