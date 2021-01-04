from django.urls import path
# from django.views.generic.base import RedirectView
from .views import TopicBlogView, TopicBlogViewTrivial
from django.conf import settings

app_name = 'topic_blog'
urlpatterns = [
    path('t/<slug:topic_slug>/', TopicBlogView.as_view(),
         name='view_topic'),
    path('s/<int:pkid>/<slug:page_slug>/', TopicBlogView.as_view(),
         name='view_article'),
    path('admin/new/', TopicBlogView.as_view(), name='new_article'),
    path('admin/edit/<slug:page_slug>', TopicBlogView.as_view(), name='edit_article'),
    path('admin/list/', TopicBlogView.as_view(), name='list_articles'),
    path('admin/list/<slug:topic_slug>', TopicBlogView.as_view(), name='list_topic'),
]

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here) to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record that with visit record.
# Need media chooser.
