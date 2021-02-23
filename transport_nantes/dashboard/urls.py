from django.urls import path
from django.conf import settings
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardIndex.as_view(), name='index'),
]
