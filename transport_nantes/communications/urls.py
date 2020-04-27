from django.urls import path

from . import views

app_name = 'communications'
urlpatterns = [
    path('', views.MainCommunications.as_view(), name='index'),
    path('b/<str:slug>', views.BlogCommunications.as_view(), name='blog'),
]
