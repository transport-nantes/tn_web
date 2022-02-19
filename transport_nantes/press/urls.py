from django.urls import path
from .views import (PressMentionListViewAdmin, PressMentionUpdateView,
                    PressMentionListView, PressMentionCreateView,
                    PressMentionDeleteView)

app_name = 'press'

urlpatterns = [
    path('', PressMentionListView.as_view(), name='view'),
    path('list/', PressMentionListViewAdmin.as_view(), name='list_items'),
    path('new/', PressMentionCreateView.as_view(), name='new_item'),
    path('update/<int:pk>', PressMentionUpdateView.as_view(), name='update_item'),
    path('delete/<int:pk>', PressMentionDeleteView.as_view(), name='delete_item'),
]
