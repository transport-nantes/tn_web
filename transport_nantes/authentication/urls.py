"""

This implements a registration and login system with the following
properties:

[TODO]
1.  Account create requests email, an optional display name (which is
the email address if not provided), and an optional password.  If not
password is provided, the account is set to login by email token.

[TODO]
2.  Login.  If the user logs in by password, we request the password.
If the user logs in by email token, we send a token, on receipt of
which we flag the user as logged in.

[TODO]
3.  Forgotten password.  Just flags the user as using email token and
sends a mail.

[TODO]
4.  Settings -> set password.  Set a password and set the user to
login by password.

[TODO]
5.  Settings -> change email.  Propose a new email, confirm on receipt
of new token.

[TODO]
6.  Logout.

This is all based on
https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html

"""
from django.urls import path
from . import views

app_name = 'authentication'
urlpatterns = [
    path('in', views.login, name='login'),
    path('out', views.DeauthView.as_view(), name='logout'),
    path('account_activation_sent/<is_new>',
         views.account_activation_sent,
         name='account_activation_sent'),
    path('activate/<token>', views.activate, name='activate'),

]
