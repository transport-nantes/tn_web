from django.urls import path

from . import views

app_name = 'asso_tn'
urlpatterns = [
    path('nous', views.QuiSommesNousView.as_view(), name='qui-sommes-nous'),
]
