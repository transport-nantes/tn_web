"""transport_nantes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from asso_tn.views import AssoView

app_name = 'legal'
urlpatterns = [
    path('mentions_legales', AssoView.as_view(template_name='legal/mentions_legales.html'),
         name='TC'),
#    path('contact', views.contact, name='contact'),
#    path('priv', views.privacy, name='privacy'),
    path('assos', AssoView.as_view(template_name='legal/aligned_orgs.html'),
         name='aligned_orgs'),
    path('sponsor', AssoView.as_view(template_name='legal/sponsor.html',
                                     hero_image="legal/sponsor.jpg"),
         name='sponsor'),
    path('benevolat', AssoView.as_view(template_name='legal/volunteer.html',
                                       hero_image="legal/bénévole.jpg"),
         name='volunteer'),
    path('jobs', AssoView.as_view(template_name='legal/jobs.html'),
         name='jobs'),
]
