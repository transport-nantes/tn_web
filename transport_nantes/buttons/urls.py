from django.urls import path
from .views import ButtonsView

app_name = 'buttons'

urlpatterns = [
    path('', ButtonsView.as_view(), name='buttons')
]