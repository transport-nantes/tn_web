from django.urls import path

from . import views

app_name = 'click_collect'
urlpatterns = [
    # This app is supposed to be general, but I'm not sure yet how
    # to do that with its templates.
    path('gr1', views.GiletReserveView.as_view(), name='gilet_reserve'),
    path('gr2', views.GiletReservedView.as_view(), name='gilet_reserved'),
]
