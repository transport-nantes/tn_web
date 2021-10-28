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
from topicblog.views import TopicBlogItemView
from django.conf import settings
from django.conf.urls.static import static
from transport_nantes.settings import ROLE

urlpatterns = [
    path('', TopicBlogItemView.as_view(), {'item_slug': 'index'},
         name='index'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('captcha/', include('captcha.urls')),
    # ClickCollect is obsolete (and we should have used mailing_list,
    # but it maybe didn't exist at the time.  But we should keep it
    # around until we recover the contacts to a periodic annoncement
    # mailing list.
    # path('cc/', include('clickcollect.urls')),
    path('d/', include('dashboard.urls')),
    path('l/', include('asso_tn.urls')),
    path('ml/', include('mailing_list.urls')),
    path('observatoire/', include('geoplan.urls')),
    # The OpenGraph app will likely be useful some day for doing
    # dynamic og/tw images.
    # path('og/', include('open_graph.urls')),
    path('questionnaire/', include('surveys.urls')),
    path('tb/', include('topicblog.urls', namespace="topicblog")),
    # The misnamed VO app has a few fragments that will be useful for
    # the OGM project.  Cf. also the benjamin-ajax-exercise branch.
    # path('??', include('velopolitain_observatoire.urls')),
    path("donation/", include('stripe_app.urls')),
]

if ROLE != 'production':
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
