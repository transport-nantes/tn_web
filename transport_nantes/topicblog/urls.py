from django.urls import path
from .views import *

app_name = 'topic_blog'
urlpatterns = [
    path('transition', Transition.as_view(), name='ADMIN_transition'),
    path('t/<slug:the_slug>/', TopicBlogItemView.as_view(),
         name='view_item_by_slug'),
    path('e/<slug:the_slug>/', TopicBlogEmailView.as_view(),
         name='view_email_by_slug'),

    path('admin/t/view/<int:pkid>/', TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid_only'),
    path('admin/e/view/<int:pkid>/', TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid_only'),

    path('admin/t/view/<int:pkid>/<slug:the_slug>/',
         TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid'),
    path('admin/e/view/<int:pkid>/<slug:the_slug>/',
         TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid'),

    path('admin/t/new/', TopicBlogItemEdit.as_view(),
         name='new_item'),
    path('admin/e/new/', TopicBlogEmailEdit.as_view(),
         name='new_email'),

    path('admin/t/edit/<int:pkid>/', TopicBlogItemEdit.as_view(),
         name='edit_item_by_pkid'),
    path('admin/e/edit/<int:pkid>/', TopicBlogEmailEdit.as_view(),
         name='edit_email_by_pkid'),

    path('admin/t/edit/<int:pkid>/<slug:the_slug>/',
         TopicBlogItemEdit.as_view(),
         name='edit_item'),
    path('admin/e/edit/<int:pkid>/<slug:the_slug>/',
         TopicBlogEmailEdit.as_view(),
         name='edit_email'),

    path('admin/t/edit/<slug:the_slug>/', TopicBlogItemEdit.as_view(),
         name='edit_item_by_slug'),
    path('admin/e/edit/<slug:the_slug>/', TopicBlogEmailEdit.as_view(),
         name='edit_email_by_slug'),

    path('admin/t/list/', TopicBlogItemList.as_view(),
         name='list_items'),
    path('admin/e/list/', TopicBlogEmailList.as_view(),
         name='list_emails'),

    path('admin/t/list/<slug:the_slug>/', TopicBlogItemList.as_view(),
         name='list_items_by_slug'),
    path('admin/e/list/<slug:the_slug>/', TopicBlogEmailList.as_view(),
         name='list_emails_by_slug'),

    path('ajax/update-template-list/', update_template_list,
         name="update_template_list"),
    path('ajax/get-slug-dict/', get_slug_dict,
         name="get_slug_dict"),
    path('ajax/get-url-list/', get_url_list,
         name="get_url_list"),
    path('ajax/get-slug-suggestions/', get_slug_suggestions,
         name="get_slug_suggestions"),
]

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here) to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record that with visit record.
# Need media chooser.
