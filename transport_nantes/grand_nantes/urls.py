from django.urls import path

from asso_tn.views import AssoView

app_name = 'grand_nantes'
urlpatterns = [
    path('', AssoView.as_view(title="La Grande Mobilité",
                              template_name='grand_nantes/index.html',
                              hero_title="La Grande Mobilité",
                              hero_image='asso_tn/images-libres/mobilité3.jpg',
                              hero_description="Me déplacer comme je veux, quand je veux",
    ),
         name='index'),
]
