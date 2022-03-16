from django.urls import path
from .views import DashboardIndex, SignatureView

app_name = 'dashboard'
urlpatterns = [
    path('', DashboardIndex.as_view(), name='index'),
    path('signature/', SignatureView.as_view(), name='signature'),
]
