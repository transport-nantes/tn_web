"""

This implements a registration and login system with the following
properties:

[Done]
1.  Create new accounts.
2.  Login with emailed magic link.
3.  Logout.

[TODO]
4.  Login by password as an option.  The code is in the template, but
    we don't currently look at it.  If it's non-empty and matches, we
    should use it and set the auth-by-email flag to False.
5.  Settings.  Permit changing email address and password as well as
    toggling auth_by_password.  Changing email or password should
    pass through a validation token.  We'll need to encrypt the
    password or else remember it.

This is all based on
https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html

"""
from django.urls import path
from . import views

app_name = 'authentication'
urlpatterns = [
    path('in', views.login, name='login'),
    path('out', views.DeauthView.as_view(), name='logout'),
    path('mod', views.profile, name='mod'),
    path('activate/<remember_me>/<token>', views.activate, name='activate'),

]
