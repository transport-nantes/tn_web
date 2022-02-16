from django.urls import path
from .views import PressMentionListViewAdmin, PressMentionListView, PressMentionCreateView

app_name = 'press'

urlpatterns = [
    path('', PressMentionListView.as_view(), name='view'),
    path('list/', PressMentionListViewAdmin.as_view(), name='list_items'),
    path('new/', PressMentionCreateView.as_view(), name='new_item'),

]
