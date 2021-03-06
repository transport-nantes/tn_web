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
from topicblog.views import TopicBlogViewTrivial

base_template = 'asso_tn/base_velopolitain.html'

urlpatterns = [
    path('', TopicBlogViewTrivial.as_view(), {'base_template': base_template},
         name='index'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls'), {'base_template': base_template}),
    path('captcha/', include('captcha.urls')),
    path('tb/', include ('topicblog.urls'), {'base_template': base_template}),
    path('l/', include('asso_tn.urls_m'), {'base_template': base_template}),
]
