from django.urls import path
from . import views

app_name = 'mobilito'

urlpatterns = [
    path('', views.MobilitoView.as_view(), name='index'),
]
