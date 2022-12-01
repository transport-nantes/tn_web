from django.urls import path
from . import views

"""
Mnemonics:
  * t  = TBItem (history)
  * e  = TBEmail
  * p  = TBPress
  * la = TBLauncher (because a solo "l" looks a bit like a 1)
"""

app_name = 'topic_blog'

topicblogitem_urls = [
    path('t/<slug:the_slug>/',
         views.TopicBlogItemView.as_view(),
         name='view_item_by_slug'),
    path('admin/t/view/<int:pkid>/',
         views.TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid_only'),
    path('admin/t/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogItemViewOne.as_view(),
         name='view_item_by_pkid'),
    path('admin/t/new/',
         views.TopicBlogItemEdit.as_view(),
         name='new_item'),
    path('admin/t/edit/<int:pkid>/',
         views.TopicBlogItemEdit.as_view(),
         name='edit_item_by_pkid'),
    path('admin/t/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogItemEdit.as_view(),
         name='edit_item'),
    path('admin/t/edit/<slug:the_slug>/',
         views.TopicBlogItemEdit.as_view(),
         name='edit_item_by_slug'),
    path('admin/t/list/',
         views.TopicBlogItemList.as_view(),
         name='list_items'),
    path('admin/t/list/<slug:the_slug>/',
         views.TopicBlogItemList.as_view(),
         name='list_items_by_slug'),
]
topicblogemail_urls = [
    path('e/<slug:the_slug>/',
         views.TopicBlogEmailView.as_view(),
         name='view_email_by_slug'),
    path('admin/e/view/<int:pkid>/',
         views.TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid_only'),
    path('admin/e/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogEmailViewOne.as_view(),
         name='view_email_by_pkid'),
    path('admin/e/new/',
         views.TopicBlogEmailEdit.as_view(),
         name='new_email'),
    path('admin/e/edit/<int:pkid>/',
         views.TopicBlogEmailEdit.as_view(),
         name='edit_email_by_pkid'),
    path('admin/e/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogEmailEdit.as_view(),
         name='edit_email'),
    path('admin/e/edit/<slug:the_slug>/',
         views.TopicBlogEmailEdit.as_view(),
         name='edit_email_by_slug'),
    path('admin/e/list/',
         views.TopicBlogEmailList.as_view(),
         name='list_emails'),
    path('admin/e/list/<slug:the_slug>/',
         views.TopicBlogEmailList.as_view(),
         name='list_emails_by_slug'),
    path('admin/e/send/<slug:the_slug>/',
         views.TopicBlogEmailSend.as_view(),
         name='send_email'),
]
topicblogpress_urls = [
    path("communiques-de-presse/",
         views.TopicBlogPressIndex.as_view(),
         name="press_releases_index"),
    path('p/<slug:the_slug>/',
         views.TopicBlogPressView.as_view(),
         name='view_press_by_slug'),
    path('admin/p/view/<int:pkid>/',
         views.TopicBlogPressViewOne.as_view(),
         name='view_press_by_pkid_only'),
    path('admin/p/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogPressViewOne.as_view(),
         name='view_press_by_pkid'),
    path('admin/p/new/',
         views.TopicBlogPressEdit.as_view(),
         name='new_press'),
    path('admin/p/edit/<int:pkid>/',
         views.TopicBlogPressEdit.as_view(),
         name='edit_press_by_pkid'),
    path('admin/p/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogPressEdit.as_view(),
         name='edit_press'),
    path('admin/p/edit/<slug:the_slug>/',
         views.TopicBlogPressEdit.as_view(),
         name='edit_press_by_slug'),
    path('admin/p/list/',
         views.TopicBlogPressList.as_view(),
         name='list_press'),
    path('admin/p/list/<slug:the_slug>/',
         views.TopicBlogPressList.as_view(),
         name='list_press_by_slug'),
    path('admin/p/send/<slug:the_slug>/',
         views.TopicBlogPressSend.as_view(),
         name='send_press'),
]
topicbloglauncher_urls = [
    path('la/<slug:the_slug>/',
         views.TopicBlogLauncherView.as_view(),
         name='view_launcher_by_slug'),
    path('admin/la/view/<int:pkid>/',
         views.TopicBlogLauncherViewOne.as_view(),
         name='view_launcher_by_pkid_only'),
    path('admin/la/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogLauncherViewOne.as_view(),
         name='view_launcher_by_pkid'),
    path('admin/la/new/',
         views.TopicBlogLauncherEdit.as_view(),
         name='new_launcher'),
    path('admin/la/edit/<int:pkid>/',
         views.TopicBlogLauncherEdit.as_view(),
         name='edit_launcher_by_pkid'),
    path('admin/la/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogLauncherEdit.as_view(),
         name='edit_launcher'),
    path('admin/la/edit/<slug:the_slug>/',
         views.TopicBlogLauncherEdit.as_view(),
         name='edit_launcher_by_slug'),
    path('admin/la/list/',
         views.TopicBlogLauncherList.as_view(),
         name='list_launcher'),
    path('admin/la/list/<slug:the_slug>/',
         views.TopicBlogLauncherList.as_view(),
         name='list_launcher_by_slug'),
]
topicblogmailinglistpitch_urls = [
    path('mlp/<slug:the_slug>/',
         views.TopicBlogMailingListPitchView.as_view(),
         name='view_mlp_by_slug'),
    path('admin/mlp/view/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogMailingListPitchViewOne.as_view(),
         name='view_mlp_by_pkid'),
    path('admin/mlp/new/',
         views.TopicBlogMailingListPitchEdit.as_view(),
         name='new_mlp'),
    path('admin/mlp/edit/<int:pkid>/',
         views.TopicBlogMailingListPitchEdit.as_view(),
         name='edit_mlp_by_pkid'),
    path('admin/mlp/edit/<int:pkid>/<slug:the_slug>/',
         views.TopicBlogMailingListPitchEdit.as_view(),
         name='edit_mlp'),
    path('admin/mlp/edit/<slug:the_slug>/',
         views.TopicBlogMailingListPitchEdit.as_view(),
         name='edit_mlp_by_slug'),
    path('admin/mlp/list/',
         views.TopicBlogMailingListPitchList.as_view(),
         name='list_mlp'),
    path('admin/mlp/list/<slug:the_slug>/',
         views.TopicBlogMailingListPitchList.as_view(),
         name='list_mlp_by_slug'),
]
topicblogpanel_urls = [
    path('panel/<slug:the_slug>/',
         views.TopicBlogPanelView.as_view(),
         name='view_panel_by_slug'),
    path("admin/panel/view/<int:pkid>/",
         views.TopicBlogPanelViewOne.as_view(),
         name="view_panel_by_pkid_only"),
    path("admin/panel/view/<int:pkid>/<slug:the_slug>/",
         views.TopicBlogPanelViewOne.as_view(),
         name="view_panel_by_pkid"),
    path("admin/panel/new/",
         views.TopicBlogPanelEdit.as_view(),
         name="new_panel"),
    path("admin/panel/edit/<int:pkid>/",
         views.TopicBlogPanelEdit.as_view(),
         name="edit_panel_by_pkid"),
    path("admin/panel/edit/<int:pkid>/<slug:the_slug>/",
         views.TopicBlogPanelEdit.as_view(),
         name="edit_panel"),
    path("admin/panel/edit/<slug:the_slug>/",
         views.TopicBlogPanelEdit.as_view(),
         name="edit_panel_by_slug"),
    path("admin/panel/list/",
         views.TopicBlogPanelList.as_view(),
         name="list_panel"),
    path("admin/panel/list/<slug:the_slug>/",
         views.TopicBlogPanelList.as_view(),
         name="list_panel_by_slug"),
]
ajax_urls = [
    path('ajax/get-slug-dict/',
         views.get_slug_dict,
         name="get_slug_dict"),
    path('ajax/get-url-list/',
         views.get_url_list,
         name="get_url_list"),
    path('ajax/get-number-of-recipients/<str:mailing_list_token>/',
         views.get_number_of_recipients,
         name="get_number_of_recipients"),
]
mail_sending_urls = [
    path('admin/self-send/',
         views.TopicBlogSelfSendView.as_view(),
         name='self_send'),
    path('e/i/<str:token>',
         views.beacon_view,
         name='beacon_view'),
]

urlpatterns = []
urlpatterns += (
    topicblogitem_urls
    + topicblogemail_urls
    + topicblogpress_urls
    + topicbloglauncher_urls
    + topicblogmailinglistpitch_urls
    + topicblogpanel_urls
    + ajax_urls
    + mail_sending_urls
)

# Need topic creation.
# Need markdown translator.
# Need click middleware (or something in view here)
# to tabulate articles served.
# Need middleware to record visit record with utm, tnclid, tntid, tnsid.
# Need to assign a tnclid to each page served and record
# that with visit record.
# Need media chooser.
