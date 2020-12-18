from django.urls import path
# from django.views.generic.base import RedirectView
from . import views
from django.contrib.sites.models import Site

site_name = Site.objects.get_current().name

app_name = 'asso_tn'
urlpatterns = [
    path('nous', views.AssoView.as_view(
        title="Qui sommes-nous ? | Transport Nantes - Association Nantaise",
        meta_descr="""<meta name="description" content="Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse."/>""",
        twitter_title = "Qui sommes-nous ? | Transport Nantes - Association Nantaise",
        twitter_descr = "Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse.",
        template_name='asso_tn/qui-sommes-nous.html',
        hero_image="asso_tn/happy-folks-1000.jpg",
        hero_title="Qui sommes-nous ?"),
         name='qui-sommes-nous'),
    path('join', views.AssoView.as_view(
        title="Nous soutenir",
        meta_descr="""<meta name="description" content="Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse."/>""",
        twitter_title = "Soutenez les Mobilitains ! | Transport Nantes - Association Nantaise",
        twitter_descr = "Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse.",
        template_name='asso_tn/join.html',
        hero_image="asso_tn/happy-folks-1000.jpg",
    ), name='join'),
    path('contact', views.AssoView.as_view(
        title="Nous contacter",
        meta_descr="""<meta name="description" content="Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse."/>""",
        twitter_title = "Qui sommes-nous ? | Transport Nantes - Association Nantaise",
        twitter_descr = "Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse.",
        template_name='asso_tn/contact.html',
        hero_image="asso_tn/happy-folks-1000.jpg"),
         name='contact'),
    path('ambassadeur', views.AssoView.as_view(
        title="Ambassadeur",
        meta_descr="""<meta name="description" content="Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse."/>""",
        twitter_title = "Qui sommes-nous ? | Transport Nantes - Association Nantaise",
        twitter_descr = "Depuis 2 ans, Transport Nantes oeuvre pour une mobilité plus sécurisée, plus fluide et plus vertueuse.",
        template_name='asso_tn/ambassadeur.html',
        hero_image="asso_tn/images-libres/pexels-andrea-piacquadio-3777952-1000.jpg",
        hero_title="Ambassadeurs Mobilitain"),
         name='ambassadeur'),
]
