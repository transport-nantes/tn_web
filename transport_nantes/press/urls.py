from django.urls import path
from . import views

app_name = 'press'

urlpatterns = [
    path('', views.PressMentionListView.as_view(), name='view'),
    path('admin/list/', views.PressMentionListViewAdmin.as_view(),
         name='list_items'),
    path('admin/new/', views.PressMentionCreateView.as_view(), name='new_item'),
    path('admin/update/<int:pk>', views.PressMentionUpdateView.as_view(),
         name='update_item'),
    path('admin/delete/<int:pk>', views.PressMentionDeleteView.as_view(),
         name='delete_item'),
    path('admin/detail/<int:pk>', views.PressMentionDetailView.as_view(),
         name='detail_item'),
    path('ajax/fetch-og-data/', views.fetch_opengraph_data, name='fetch_og_data'),
]
