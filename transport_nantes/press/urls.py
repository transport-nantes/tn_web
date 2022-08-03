from django.urls import path
from .views import (PressMentionListViewAdmin, PressMentionUpdateView,
                    PressMentionListView, PressMentionCreateView,
                    PressMentionDeleteView, PressMentionDetailView)

app_name = 'press'

urlpatterns = [
    path('', PressMentionListView.as_view(), name='view'),
    path('admin/list/', PressMentionListViewAdmin.as_view(),
         name='list_items'),
    path('admin/new/', PressMentionCreateView.as_view(), name='new_item'),
    path('admin/update/<int:pk>', PressMentionUpdateView.as_view(),
         name='update_item'),
    path('admin/delete/<int:pk>', PressMentionDeleteView.as_view(),
         name='delete_item'),
    path('admin/detail/<int:pk>', PressMentionDetailView.as_view(),
         name='detail_item'),
]
