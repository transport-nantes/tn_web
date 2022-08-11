from django.urls import path
from dashboard import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.DashboardIndex.as_view(), name='index'),
    path('signature/', views.SignatureView.as_view(), name='signature'),
    path('email-campaigns/', views.EmailCampaignsDashboardView.as_view(),
         name='email_campaigns'),
    path('email-campaigns/user/<int:pk>/',
         views.UserSendRecordsDetailView.as_view(),
         name='user_send_records'),
    path('email-campaigns/<int:pk>/', views.EmailCampaignDetailView.as_view(),
         name='email_campaign_details'),
]
