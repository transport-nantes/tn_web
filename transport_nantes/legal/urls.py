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
from . import views

app_name = 'legal'
urlpatterns = [
    path('mentions_legales', views.MentionsLegalesView.as_view(), name='TC'),
#    path('contact', views.contact, name='contact'),
#    path('priv', views.privacy, name='privacy'),
    path('assos', views.AlignedOrgsView.as_view(), name='aligned_orgs'),
    path('sponsor', views.SponsorView.as_view(), name='sponsor'),
    path('benevolat', views.VolunteerView.as_view(), name='volunteer'),
    path('jobs', views.JobsView.as_view(), name='jobs'),
]
