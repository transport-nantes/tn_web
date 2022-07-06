from django.urls import path
from . import views

app_name = 'mobilito'

urlpatterns = [
    path('', views.MobilitoView.as_view(), name='index'),
    path('tutoriel/', views.TutorialView.as_view(), name='tutorial'),
    path('formulaire-adresse/',
         views.AddressFormView.as_view(),
         name='address_form'),
]
