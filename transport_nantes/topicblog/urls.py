from django.urls import path
# from django.views.generic.base import RedirectView
from .views import TopicBlogLegacyView
from .views import TopicBlogItemEdit
from transport_nantes.settings import ROLE

app_name = 'topic_blog'
urlpatterns = [
    path('t/<slug:topic_slug>/', TopicBlogLegacyView.as_view(),
         name='view_topic'),
]
if ROLE != 'production':
    # beta and dev
    urlpatterns += [
        path('admin/new/',
             TopicBlogItemEdit.as_view(),
             name='new_item'),
        path('admin/edit/<int:pkid>/',
             TopicBlogItemEdit.as_view(),
             name='edit_item_no_slug'),
        path('admin/edit/<int:pkid>/<slug:item_slug>/',
             TopicBlogItemEdit.as_view(),
             name='edit_item'),
        path('admin/edit/<slug:item_slug>/',
             TopicBlogItemEdit.as_view(),
             name='edit_item_slug'),
        ]

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here) to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record that with visit record.
# Need media chooser.
