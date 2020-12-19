from django.urls import path

from asso_tn.views import AssoView

app_name = 'grand_nantes'
urlpatterns = [
    path('', AssoView.as_view(
        title="Transport Nantes | La Grande Mobilité - Optimiser le maillage global",
        meta_descr="""<meta name="description" content="La Grande Mobilité c’est considérer l’ensemble des solutions de mobilités actives et douces. "/>""",
        twitter_title = "Transport Nantes | La Grande Mobilité - Optimiser le maillage global",
        twitter_descr = "La Grande Mobilité c’est considérer l’ensemble des solutions de mobilités actives et douces.",
        twitter_image = "asso_tn/accueil-mobilité-multimodale.jpg",
        template_name='grand_nantes/index.html',
        hero_title="La Grande Mobilité",
        hero_image='asso_tn/images-libres/mobilité3.jpg',
        hero_description="Me déplacer comme je veux, quand je veux",
    ),
         name='index'),
]
