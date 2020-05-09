from django.urls import path

from . import views

app_name = 'cluster_blog'
urlpatterns = [
    path('e/<str:slug>', views.MainClusterBlog.as_view(),
         name='deconfinement'),
    path('EbyC/<int:cluster>/<int:category>', views.CategoryClusterBlog.as_view(),
         name='deconfinement_role'),
]
