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
from django.contrib.auth import views as auth_views

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

    # Paths below must be here because of django architecture
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'),
        name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),
]
