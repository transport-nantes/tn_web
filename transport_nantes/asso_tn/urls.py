from django.urls import path

# from django.views.generic.base import RedirectView
from . import views

app_name = "asso_tn"
urlpatterns = [
    path(
        "nous-contacter",
        views.AssoView.as_view(
            title="Nous contacter",
            meta_descr=(
                """<meta name="description" content="Les Mobilitains """
                """oeuvrent pour une mobilité plus sécurisée, plus fluide et"""
                """ plus vertueuse."/>"""
            ),
            twitter_title="Qui sommes-nous ? | Mobilitains",
            twitter_descr=(
                "Les Mobilitains oeuvrent pour une mobilité plus "
                "sécurisée, plus fluide et plus vertueuse."
            ),
            template_name="asso_tn/contact.html",
            hero_image="asso_tn/happy-folks-1000.jpg",
        ),
        name="contact",
    ),
    # This has a first commit in #12, then some emails exchanged with Julien.
    # What's here is a place holder.
    path(
        "mentions-legales",
        views.AssoView.as_view(
            title="Mentions Légales",
            template_name="asso_tn/mentions_legales.html",
        ),
        name="TC",
    ),
    # Copyright page needed.
    path(
        "jobs",
        views.AssoView.as_view(
            title="Jobs",
            template_name="asso_tn/jobs.html",
            meta_descr=(
                """<meta name="description" content="Les Mobilitains """
                """oeuvrent pour une mobilité plus sécurisée, plus fluide et"""
                """ plus vertueuse."/>"""
            ),
            twitter_title=(
                "Les Mobilitains cherchent un-e chargé-e de com militant-e."
            ),
            twitter_descr=(
                "Ensemble changeons la mobilité dans la région nantaise,"
                " les Pays de la Loire et le Grand Ouest."
            ),
            hero_image="asso_tn/images-quentin-boulegon/pont-rousseau-1.jpg",
        ),
        name="jobs",
    ),
    path(
        "crowdfunding-2021",
        views.AssoView.as_view(
            title="Collecte de dons pour la mobilité",
            meta_descr=(
                """<meta name="description" content="Les Mobilitains font"""
                """ un Crowdfunding pour ceux qui veulent faire de la"""
                """ mobilité plus sécurisée, plus fluide et plus"""
                """vertueuse."/>"""
            ),
            twitter_title="Crowdfunding | Mobilitains",
            twitter_descr=(
                "Les Mobilitains font un Crowdfunding pour ceux qui"
                " veulent faire de la mobilité plus sécurisée, plus fluide et"
                " plus vertueuse."
            ),
            template_name="asso_tn/crowdfunding.html",
            hero_image=(
                "asso_tn/crowdfunding_2021/00-heroimage-crowdfunding.jpg"
            ),
            hero_title="Collecte de dons pour la mobilité",
            hero_description=(
                "Multiplions la fréquence de nos bus, TGV," " tramway et TER !"
            ),
            # hero_description="et comment c'est chouette !",
            # hero_description="et comment c'est chouette !",
            # hero_description="tout le monde est avec !",
        ),
        name="crowdfunding-2021",
    ),
    path(
        "edit-username/<str:username>",
        views.EditUsernameView.as_view(),
        name="edit_username",
    ),
    path(
        "preferences/",
        views.PreferencesView.as_view(),
        name="preferences",
    ),
]
