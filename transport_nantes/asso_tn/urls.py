from django.urls import path

from . import views

app_name = 'asso_tn'
urlpatterns = [
    path('nous', views.AssoView.as_view(template_name='asso_tn/qui-sommes-nous.html',
                                        hero_image="asso_tn/happy-folks-1000.jpg"),
         name='qui-sommes-nous'),
    path('join', views.AssoView.as_view(template_name='asso_tn/join.html',
                                        hero_image="asso_tn/happy-folks-1000.jpg"),
         name='join'),
    path('contact', views.AssoView.as_view(template_name='asso_tn/contact.html',
                                           hero_image="asso_tn/happy-folks-1000.jpg"),
         name='contact'),
    path('ambassadeur', views.AssoView.as_view(template_name='asso_tn/ambassadeur.html',
                                               hero_image="asso_tn/images-libres/pexels-andrea-piacquadio-3777952-1000.jpg"),
         name='ambassadeur'),
]
