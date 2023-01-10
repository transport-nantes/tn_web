from django.urls import path
from . import views

"""
Application to manage a photo competition.

In the first iteration of the application, we assume a single photo
competition in all of history.  If we repeat, we'll add
database-driven concepts of which competition and so forth.

"""

app_name = "photo"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("upload/", views.UploadEntry.as_view(), name="upload"),
    path("confirmation/", views.Confirmation.as_view(), name="confirmation"),
    path("galerie/", views.PhotoListView.as_view(), name="galerie"),
    path(
        "galerie/<str:photo_sha1>",
        views.PhotoView.as_view(),
        name="photo_details",
    ),
    path(
        "galerie/n/<str:photo_sha1>",
        views.NextPhotoView.as_view(),
        name="next_photo_details",
    ),
    path(
        "galerie/p/<str:photo_sha1>",
        views.PrevPhotoView.as_view(),
        name="prev_photo_details",
    ),
]
