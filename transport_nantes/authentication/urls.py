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
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'authentication'
urlpatterns = [
    path('in', views.login, name='login'),
    path('out', views.DeauthView.as_view(), name='logout'),
    path('mod', views.profile, name='mod'),
    path('account_activation_sent/<is_new>',
         views.account_activation_sent,
         name='account_activation_sent'),
    path('activate/<token>', views.activate, name='activate'),

    path('password_reset/', views.CustomPasswordReset.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'),
        name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirm.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'),
        name='password_reset_complete'),

]
