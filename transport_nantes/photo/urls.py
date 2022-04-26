from django.urls import path
from . import views

"""
Application to manage a photo competition.

In the first iteration of the application, we assume a single photo
competition in all of history.  If we repeat, we'll add
database-driven concepts of which competition and so forth.

"""

app_name = 'photo'
urlpatterns = [
    path('upload/', views.UploadEntry.as_view(),
         name='upload'),
    path('confirmation/', views.Confirmation.as_view(),
         name='confirmation'),
]
