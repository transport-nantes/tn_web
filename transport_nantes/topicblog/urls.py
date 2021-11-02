from django.urls import path
# from django.views.generic.base import RedirectView
from .views import (TopicBlogItemEdit, TopicBlogItemView, TopicBlogItemViewOne,
                    TopicBlogItemList)
from .views import (update_template_list, get_slug_dict, get_url_list)
# from transport_nantes.settings import ROLE

app_name = 'topic_blog'
urlpatterns = [
    path('t/<slug:item_slug>/', TopicBlogItemView.as_view(),
         name='view_item_by_slug'),

    path('admin/view/<int:pkid>/', TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid_only'),
    path('admin/view/<int:pkid>/<slug:item_slug>/',
         TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid'),

    path('admin/new/', TopicBlogItemEdit.as_view(),
         name='new_item'),
    path('admin/edit/<int:pkid>/', TopicBlogItemEdit.as_view(),
         name='edit_item_by_pkid'),
    path('admin/edit/<int:pkid>/<slug:item_slug>/',
         TopicBlogItemEdit.as_view(),
         name='edit_item'),
    path('admin/edit/<slug:item_slug>/', TopicBlogItemEdit.as_view(),
         name='edit_item_by_slug'),

    path('admin/list/', TopicBlogItemList.as_view(),
         name='list_items'),
    path('admin/list/<slug:item_slug>/', TopicBlogItemList.as_view(),
         name='list_items_by_slug'),

    path('ajax/update-template-list/', update_template_list,
         name="update_template_list"),
    path('ajax/get-slug-dict/', get_slug_dict,
         name="get_slug_dict"),
    path('ajax/get-url-list/', get_url_list,
         name="get_url_list"),
]

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here) to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record that with visit record.
# Need media chooser.
