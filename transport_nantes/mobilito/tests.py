from datetime import datetime, timezone

from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse_lazy

from .models import Session, MobilitoUser


class SessionViewTests(TestCase):

    def setUp(self):
        # Creation of a Session object
        user = User.objects.create(username='foo', password='bar')
        self.user = MobilitoUser.objects.create(user=user)
        self.session = Session.objects.create(
            user=self.user,
            start_timestamp=datetime.now(timezone.utc),
        )
        self.session_url = reverse_lazy(
            'mobilito:session_summary', args=[self.session.session_sha1])

        # User with permission to view unpublished sessions
        self.authorised_user = User.objects.create(username='bar', password='foo')
        may_view_sessions = Permission.objects.get(codename="session.view_session")
        self.authorised_user.user_permissions.add(may_view_sessions)

        # Creating 3 clients for each user type :
        # - author_client : Is the mobilito Session's author
        # - authorised_client : Is a user with the permission to view the session
        # - Anonymous client : Is a user without the permission to view the session
        self.author_client = Client()
        self.author_client.force_login(user)
        self.anonymous_client = Client()
        self.authorised_user_client = Client()
        self.authorised_user_client.force_login(self.authorised_user)

        # Client - Code pairs for DRYer code. These are list of dicts that
        # contain the client to use and the expected response code in
        # standard cases (e.g. the page doesn't require permission to be
        # viewed...)
        self.perm_needed_responses = [
            {"client": self.author_client, "code": 200,
             "msg": "Session's author is able to see this page"},
            {"client": self.anonymous_client, "code": 404,
             "msg": ("Users without proper permissions can't have "
                     "access to this page.")},
            {"client": self.authorised_user_client, "code": 200,
             "msg": "The page must return 200 the user has the permission."}
        ]
        self.no_perm_needed_responses = [
            {"client": self.author_client, "code": 200,
             "msg": "The page must return 200, permission is not mandatory."},
            {"client": self.anonymous_client, "code": 200,
             "msg": "The page must return 200, permission is not mandatory."},
            {"client": self.authorised_user_client, "code": 200,
             "msg": "The page must return 200, permission is not mandatory."}
        ]

    def test_session_view(self):
        """Test the ability to see a session that is published and doesn't
        require permission."""
        for client_code in self.no_perm_needed_responses:
            response = client_code["client"].get(self.session_url)
            self.assertEqual(
                response.status_code, client_code["code"], client_code["msg"])

    def test_session_view_unpublished(self):
        """Test the ability to see a session that is not published."""
        self.session.published = False
        self.session.save()
        for client_code in self.perm_needed_responses:
            response = client_code["client"].get(self.session_url)
            self.assertEqual(
                response.status_code, client_code["code"], client_code["msg"])
