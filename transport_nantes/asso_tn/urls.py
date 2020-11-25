from django.urls import path

from . import views

app_name = 'asso_tn'
urlpatterns = [
    path('nous', views.AssoView.as_view(title="Qui sommes-nous ?",
                                        template_name='asso_tn/qui-sommes-nous.html',
                                        hero_image="asso_tn/happy-folks-1000.jpg",
                                        hero_title="Qui sommes-nous ?"),
         name='qui-sommes-nous'),
    path('join', views.AssoView.as_view(title="Adhésion",
                                        template_name='asso_tn/join.html',
                                        hero_image="asso_tn/happy-folks-1000.jpg",
                                        hero_title="Envie d'en être ?",
                                        hero_description="Nous sommes plus fort ensemble"),
         name='join'),
    path('contact', views.AssoView.as_view(title="Nous contacter",
                                           template_name='asso_tn/contact.html',
                                           hero_image="asso_tn/happy-folks-1000.jpg"),
         name='contact'),
    path('ambassadeur', views.AssoView.as_view(title="Ambassadeur",
                                               template_name='asso_tn/ambassadeur.html',
                                               hero_image="asso_tn/images-libres/pexels-andrea-piacquadio-3777952-1000.jpg",
                                               hero_title="Ambassadeurs Mobilitain"),
         name='ambassadeur'),
]
