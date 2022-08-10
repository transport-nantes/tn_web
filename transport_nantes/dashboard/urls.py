from django.urls import path
from dashboard import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.DashboardIndex.as_view(), name='index'),
    path('signature/', views.SignatureView.as_view(), name='signature'),
    path('email-campaigns/', views.EmailCampaignsDashboardView.as_view(),
         name='email_campaigns'),
]
