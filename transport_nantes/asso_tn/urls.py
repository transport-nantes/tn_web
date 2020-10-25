from django.urls import path

from . import views

app_name = 'asso_tn'
urlpatterns = [
    path('nous', views.AssoView.as_view(template_name='asso_tn/qui-sommes-nous.html'),
         name='qui-sommes-nous'),
    path('join', views.AssoView.as_view(template_name='asso_tn/join.html'), name='join'),
    path('contact', views.AssoView.as_view(template_name='asso_tn/contact.html'), name='contact'),
]
