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
from django.contrib import admin
from django.urls import include, path
from asso_tn.views import MainTransportNantes

urlpatterns = [
    path('', MainTransportNantes.as_view(), name='index'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('captcha/', include('captcha.urls')),
    path('cb/', include('clusterblog.urls')),
    path('cc/', include('clickcollect.urls')),
    path('cp/', include('communications.urls')),
    path('gn/', include('grand_nantes.urls')),
    path('j/', include('legal.urls')),
    path('ml/', include('mailing_list.urls')),
    path('observatoire/', include('observatoire.urls')),
    path('og/', include('open_graph.urls')),
    path('surveys/', include('surveys.urls')),
    path('tn/', include('asso_tn.urls')),
    path('v/', include('velopolitain.urls')),
    path('vo/', include('velopolitain_observatoire.urls')),
]
