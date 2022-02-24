from django.urls import path
from . import views

app_name = 'topic_blog'
urlpatterns = [
    path('t/<slug:the_slug>/', views.TopicBlogItemView.as_view(),
         name='view_item_by_slug'),
    path('e/<slug:the_slug>/', views.TopicBlogEmailView.as_view(),
         name='view_email_by_slug'),

    path('admin/t/view/<int:pkid>/', views.TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid_only'),
    path('admin/e/view/<int:pkid>/', views.TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid_only'),

    path('admin/t/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid'),
    path('admin/e/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid'),

    path('admin/t/new/', views.TopicBlogItemEdit.as_view(),
         name='new_item'),
    path('admin/e/new/', views.TopicBlogEmailEdit.as_view(),
         name='new_email'),

    path('admin/t/edit/<int:pkid>/', views.TopicBlogItemEdit.as_view(),
         name='edit_item_by_pkid'),
    path('admin/e/edit/<int:pkid>/', views.TopicBlogEmailEdit.as_view(),
         name='edit_email_by_pkid'),

    path('admin/t/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogItemEdit.as_view(),
         name='edit_item'),
    path('admin/e/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogEmailEdit.as_view(),
         name='edit_email'),

    path('admin/t/edit/<slug:the_slug>/', views.TopicBlogItemEdit.as_view(),
         name='edit_item_by_slug'),
    path('admin/e/edit/<slug:the_slug>/', views.TopicBlogEmailEdit.as_view(),
         name='edit_email_by_slug'),

    path('admin/t/list/', views.TopicBlogItemList.as_view(),
         name='list_items'),
    path('admin/e/list/', views.TopicBlogEmailList.as_view(),
         name='list_emails'),

    path('admin/t/list/<slug:the_slug>/', views.TopicBlogItemList.as_view(),
         name='list_items_by_slug'),
    path('admin/e/list/<slug:the_slug>/', views.TopicBlogEmailList.as_view(),
         name='list_emails_by_slug'),

    path('admin/e/send/<int:pkid>/<slug:the_slug>/<str:mailing_list_token>/',
         views.TopicBlogEmailSendMail.as_view(),
         name='send_email'),

    path('ajax/get-slug-dict/', views.get_slug_dict,
         name="get_slug_dict"),
    path('ajax/get-url-list/', views.get_url_list,
         name="get_url_list"),
    path('ajax/get-slug-suggestions/', views.get_slug_suggestions,
         name="get_slug_suggestions"),
]

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here)
# to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record
# that with visit record.
# Need media chooser.
