from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.contrib.auth.models import Permission, User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import TopicBlogEmail, TopicBlogLauncher
from .models import TopicBlogObjectBase as TBObject
from .models import TopicBlogPanel, TopicBlogPress


class TBETest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username="test-user", password="test-pass"
        )
        self.user.save()
        # Create a user with all permission
        self.staff = User.objects.create_user(
            username="test-staff", password="test-staff"
        )

        edit_permission = Permission.objects.get(codename="tbe.may_edit")
        view_permission = Permission.objects.get(codename="tbe.may_view")
        publish_permission = Permission.objects.get(codename="tbe.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbe.may_publish_self"
        )
        self.staff.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission,
        )
        self.staff.save()
        # Create client and log user into the client
        self.user_client = Client()
        self.staff_client = Client()

        self.user_client.login(username="test-user", password="test-pass")
        self.staff_client.login(username="test-staff", password="test-staff")

        # Create Topiclog email object
        self.template_email = "topicblog/content_email.html"
        self.email_with_slug = TopicBlogEmail.objects.create(
            slug="email",
            subject="subject",
            body_text_1_md="body",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.staff,
            template_name=self.template_email,
            title="Test-title",
        )

        self.email_without_slug = TopicBlogEmail.objects.create(
            subject="subject2",
            body_text_1_md="body2",
            user=self.staff,
            template_name=self.template_email,
            title="Test-title",
        )

    """ TESTING MODEL"""

    def test_str_func(self):
        good_str_with_slug = (
            f"{self.email_with_slug.slug} - "
            f"{self.email_with_slug.title} - "
            f"ID : {self.email_with_slug.id}"
        )
        self.assertEqual(self.email_with_slug.__str__(), good_str_with_slug)
        good_str_without_slug = (
            f"{self.email_without_slug.title} - "
            f"ID : {self.email_without_slug.id} "
            "(NO SLUG)"
        )
        self.assertEqual(
            self.email_without_slug.__str__(), good_str_without_slug
        )

    """ TESTING VIEW """

    def test_view_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_slug",
                    kwargs={
                        "the_slug": self.email_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

        # with bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_slug",
                    kwargs={
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_email_by_pkid_only(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid_only",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid but item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the item have no slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid_only",
                    kwargs={
                        "pkid": self.email_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " a good pkid",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid_only",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_email_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                        "the_slug": self.email_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_email_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_new_email(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if user have the"
                " have the permission",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(reverse("topicblog:new_email"))
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_emails(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_emails")
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_items_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse(
                    "topicblog:list_emails_by_slug",
                    kwargs={
                        "the_slug": self.email_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_email_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email_by_pkid",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid and item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid a slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email_by_pkid",
                    kwargs={
                        "pkid": self.email_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " wrong pkid.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_email(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                        "the_slug": self.email_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email",
                    kwargs={
                        "pkid": self.email_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_email",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )


class TBPTest(TestCase):
    def setUp(self):

        TBETest.setUp(self)
        edit_permission = Permission.objects.get(codename="tbp.may_edit")
        view_permission = Permission.objects.get(codename="tbp.may_view")
        publish_permission = Permission.objects.get(codename="tbp.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbp.may_publish_self"
        )
        self.staff.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission,
        )
        self.staff.save()

        # Create Topiclog press object
        self.template_press = "topicblog/content_press.html"
        self.press_with_slug = TopicBlogPress.objects.create(
            slug="press",
            subject="subject",
            body_text_1_md="body",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.staff,
            template_name=self.template_press,
            title="Test-title",
        )
        self.press_without_slug = TopicBlogPress.objects.create(
            subject="subject1",
            body_text_1_md="body1",
            user=self.staff,
            template_name=self.template_press,
            title="Test-title",
        )

    """ TESTING MODEL"""

    def test_str_func(self):
        good_str_with_slug = (
            f"{self.press_with_slug.slug} - "
            f"{self.press_with_slug.title} - "
            f"ID : {self.press_with_slug.id}"
        )
        self.assertEqual(self.press_with_slug.__str__(), good_str_with_slug)
        good_str_without_slug = (
            f"{self.press_without_slug.title} - "
            f"ID : {self.press_without_slug.id} "
            "(NO SLUG)"
        )
        self.assertEqual(
            self.press_without_slug.__str__(), good_str_without_slug
        )

    """ TESTING VIEW """

    def test_view_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_slug",
                    kwargs={
                        "the_slug": self.press_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

        # with bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_slug",
                    kwargs={
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_press_by_pkid_only(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid_only",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid but item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the item have no slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid_only",
                    kwargs={
                        "pkid": self.press_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " a good pkid",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid_only",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_press_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                        "the_slug": self.press_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_press_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_new_press(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if user have the"
                " have the permission",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(reverse("topicblog:new_press"))
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_presss(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(reverse("topicblog:list_press"))
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_press_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse(
                    "topicblog:list_press_by_slug",
                    kwargs={
                        "the_slug": self.press_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_press_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press_by_pkid",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid and item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid a slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press_by_pkid",
                    kwargs={
                        "pkid": self.press_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " wrong pkid.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_press(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                        "the_slug": self.press_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press",
                    kwargs={
                        "pkid": self.press_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_press",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_press_release_index(self):
        now = datetime.now()
        published_press_release = TopicBlogPress.objects.create(
            title="Published Press Release",
            slug="published-press-release",
            body_text_1_md="This is the body",
            publication_date=now,
            user=self.staff,
            template_name=self.template_press,
        )
        older_published_press_release = TopicBlogPress.objects.create(
            title="Older Press Release",
            slug="published-press-release",
            body_text_1_md="This is the body",
            publication_date=now - timedelta(days=1),
            user=self.staff,
            template_name=self.template_press,
        )
        published_press_release_with_different_slug = (
            TopicBlogPress.objects.create(
                title="Different Slug Press Release",
                slug="published-press-release-with-different-slug",
                body_text_1_md="This is the body",
                publication_date=now,
                user=self.staff,
                template_name=self.template_press,
            )
        )
        unpublished_press_release = TopicBlogPress.objects.create(
            title="Unpublished Press Release",
            slug="unpublished-press-release",
            body_text_1_md="This is the body",
            publication_date=None,
            user=self.staff,
            template_name=self.template_press,
        )

        url = reverse("topicblog:press_releases_index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, published_press_release.title, count=1)
        self.assertContains(
            response,
            published_press_release_with_different_slug.title,
            count=1,
        )
        self.assertNotContains(response, unpublished_press_release.title)
        self.assertNotContains(response, older_published_press_release.title)


class TBLATest(TestCase):
    def setUp(self):

        TBETest.setUp(self)
        edit_permission = Permission.objects.get(codename="tbla.may_edit")
        view_permission = Permission.objects.get(codename="tbla.may_view")
        publish_permission = Permission.objects.get(
            codename="tbla.may_publish"
        )
        publish_self_permission = Permission.objects.get(
            codename="tbla.may_publish_self"
        )
        self.staff.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission,
        )
        self.staff.save()

        # Create Topiclog launcher object
        self.template_launcher = "topicblog/content_launcher.html"
        self.launcher_with_slug = TopicBlogLauncher.objects.create(
            slug="launcher",
            launcher_image="picture.png",
            launcher_image_alt_text="picture",
            launcher_text_md="laucher text",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.staff,
            template_name=self.template_launcher,
            headline="Headline",
        )

        self.launcher_without_slug = TopicBlogLauncher.objects.create(
            user=self.staff,
            launcher_image="picture1.png",
            launcher_image_alt_text="picture1",
            launcher_text_md="laucher text1",
            template_name=self.template_launcher,
            headline="Headline 1",
        )

    """ TESTING MODEL"""

    def test_str_func(self):
        good_str_with_slug = (
            f"{self.launcher_with_slug.headline} - "
            f"ID : {self.launcher_with_slug.id}"
        )
        self.assertEqual(self.launcher_with_slug.__str__(), good_str_with_slug)
        good_str_without_slug = (
            f"{self.launcher_without_slug.headline} - "
            f"ID : {self.launcher_without_slug.id}"
        )
        self.assertEqual(
            self.launcher_without_slug.__str__(), good_str_without_slug
        )

    """ TESTING VIEW """

    def test_view_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the the good"
                " slug.",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_slug",
                    kwargs={
                        "the_slug": self.launcher_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

        # with bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we provide a "
                "wrong slug not related to any item.",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_slug",
                    kwargs={
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_launcher_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                        "the_slug": self.launcher_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_new_launcher(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if user have the"
                " have the permission",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:new_launcher")
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_launchers(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_launcher")
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_list_items_by_slug(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        users_expected = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide no parameters.",
            },
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse(
                    "topicblog:list_launcher_by_slug",
                    kwargs={
                        "the_slug": self.launcher_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_view_launcher_by_pkid_only(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid_only",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid but item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the item have no slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid_only",
                    kwargs={
                        "pkid": self.launcher_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " a good pkid",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:view_launcher_by_pkid_only",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_launcher_by_pkid(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid but the item have a slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher_by_pkid",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid and item have no slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth.",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid a slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher_by_pkid",
                    kwargs={
                        "pkid": self.launcher_without_slug.id,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " wrong pkid.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher_by_pkid",
                    kwargs={
                        "pkid": 999999999,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )

    def test_edit_launcher(self):
        """ "For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 200,
                "msg": "The page MUST return 200 if we provide the"
                " good pkid and the good slug",
            },
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                        "the_slug": self.launcher_with_slug.slug,
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with good pkid bad slug
        users_expected_1 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page MUST return 404 if we provide the"
                " good pkid and and the wrong slug",
            },
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher",
                    kwargs={
                        "pkid": self.launcher_with_slug.id,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )
        # with bad pkid and bad slug
        users_expected_2 = [
            {
                "client": self.user_client,
                "code": 403,
                "msg": "Normal users can't access this page.",
            },
            {
                "client": self.client,
                "code": 302,
                "msg": "The page should return 302 if not auth",
            },
            {
                "client": self.staff_client,
                "code": 404,
                "msg": "The page should return 404 if we don't provide"
                " good pkid and slug.",
            },
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse(
                    "topicblog:edit_launcher",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "bad-slug",
                    },
                )
            )
            self.assertEqual(
                response.status_code, user_type["code"], msg=user_type["msg"]
            )


class MoribundAndDelete(TestCase):
    def setUp(self):
        TBETest.setUp(self)
        now = datetime.now(timezone.utc)
        then_moribund = now - timedelta(days=TBObject.K_MORIBUND_DELAY_DAYS)
        then_deletable = (
            now
            - timedelta(days=TBObject.K_MORIBUND_DELAY_DAYS)
            - timedelta(days=TBObject.K_MORIBUND_CLEARED_FOR_DELETING_DAYS)
        )
        self.moribund_email = TopicBlogEmail.objects.create(
            slug="email",
            subject="slug2",
            body_text_1_md="body",
            user=self.user,
            template_name=self.template_email,
            title="Test-title",
        )
        self.moribund_email.date_created = then_moribund
        self.deletable_email = TopicBlogEmail.objects.create(
            slug="email",
            subject="slug2",
            body_text_1_md="body",
            user=self.user,
            template_name=self.template_email,
            title="Test-title",
            scheduled_for_deletion_date=then_deletable,
        )
        self.deletable_email.date_created = then_deletable
        self.email_ok = TopicBlogEmail.objects.create(
            slug="email",
            subject="slug2",
            body_text_1_md="body",
            user=self.user,
            template_name=self.template_email,
            title="Test-title",
        )

    def test_moribund_and_delete(self):
        self.assertTrue(self.moribund_email.is_moribund())
        self.assertTrue(self.deletable_email.is_moribund())
        self.assertFalse(self.email_ok.is_moribund())


class TopicBlogPanelsViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
        )

        self.authorized_user = User.objects.create(
            username="authorized_user",
        )
        may_view = Permission.objects.get(codename="tbpanel.may_view")
        may_edit = Permission.objects.get(codename="tbpanel.may_edit")
        may_publish = Permission.objects.get(codename="tbpanel.may_publish")
        may_publish_self = Permission.objects.get(
            codename="tbpanel.may_publish_self"
        )
        self.authorized_user.user_permissions.add(
            may_view, may_edit, may_publish, may_publish_self
        )

        self.authorized_user_client = Client()
        self.authorized_user_client.force_login(self.authorized_user)

        self.unauthorized_user = User.objects.create(
            username="unauthorized_user",
        )
        self.no_permissions_client = Client()
        self.no_permissions_client.force_login(self.unauthorized_user)

        # Image that can be used to fake a file upload
        THIS_DIR = Path(__file__).resolve().parent
        FILE_PATH = THIS_DIR / "test_data" / "300x300.png"
        with open(FILE_PATH, "rb") as f:
            content = f.read()

        self.uploaded_image = SimpleUploadedFile(
            name="test_image.png", content=content, content_type="image/png"
        )

        FILE_PATH_2 = THIS_DIR / "test_data" / "250x250.png"
        # Image that can be used as an image in TBPanels
        # No context manager used here, because the file must be open
        # when the test is run. The file is closed in the tearDown method.
        self.content_2 = open(FILE_PATH_2, "rb")
        self.image = ImageFile(self.content_2, name="250x250.png")

        self.published_panel = TopicBlogPanel.objects.create(
            title="Test Panel Title",
            slug="test-panel",
            body_text_1_md="**This is a published test panel.**",
            body_image_1=self.image,
            body_image_1_alt_text="Test image",
            user=self.user,
            template_name="topicblog/panel_did_you_know_tip_1.html",
            publication_date=datetime.now(timezone.utc),
            publisher=self.user,
        )
        self.unpublished_panel = TopicBlogPanel.objects.create(
            title="Test Panel Title",
            slug="test-panel",
            body_text_1_md="**This is an unpublished panel.**",
            user=self.user,
            template_name="topicblog/panel_did_you_know_tip_1.html",
        )
        self.slugless_panel = TopicBlogPanel.objects.create(
            title="Test Panel Title",
            body_text_1_md="**This is a slugless panel.**",
            user=self.user,
            template_name="topicblog/panel_did_you_know_tip_1.html",
        )

        # Anonymous users are invited to log in and from there, you
        # land either on 403 Forbidden or 200 OK depending on the
        # user's permissions.
        self.perm_needed_responses = [
            {
                "client": self.client,
                "code": 302,
                "msg": "Anonymous users are redirected to login.",
            },
            {
                "client": self.authorized_user_client,
                "code": 200,
                "msg": (
                    "Logged in users with proper permissions can have "
                    "access to this page."
                ),
            },
            {
                "client": self.no_permissions_client,
                "code": 403,
                "msg": (
                    "Logged in users without proper permissions can't have "
                    "access to this page."
                ),
            },
        ]
        self.no_perm_needed_responses = [
            {
                "client": self.client,
                "code": 200,
                "msg": "The page must return 200 independently of permissions.",
            },
            {
                "client": self.authorized_user_client,
                "code": 200,
                "msg": "The page must return 200 independently of permissions.",
            },
            {
                "client": self.no_permissions_client,
                "code": 200,
                "msg": "The page must return 200 independently of permissions.",
            },
        ]

    def tearDown(self):
        self.content_2.close()

    def test_view_panel_by_slug(self):
        """Test that the panel view returns the correct panel."""
        url = reverse(
            "topicblog:view_panel_by_slug", kwargs={"the_slug": "test-panel"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a published test panel.")

        # We now publish the unpublished panel and check that it is visible
        self.unpublished_panel.publish()
        self.unpublished_panel.save()

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is an unpublished panel.")

        # Test that the panel view returns 404 for a bad slug.
        url = reverse(
            "topicblog:view_panel_by_slug", kwargs={"the_slug": "bad-slug"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_view_panel_by_pkid_only(self):
        """Test that the panel ViewOne returns the correct panel."""
        url = reverse(
            "topicblog:view_panel_by_pkid_only",
            kwargs={"pkid": self.slugless_panel.id},
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )
            if response.status_code == 200:
                self.assertContains(response, self.slugless_panel.title)

        # Test that the panel view returns 404 for a bad pkid.
        url = reverse(
            "topicblog:view_panel_by_pkid_only", kwargs={"pkid": 999999999}
        )
        response = self.authorized_user_client.get(url)

        self.assertEqual(response.status_code, 404)

        # Test status code for panels with slug
        url = reverse(
            "topicblog:view_panel_by_pkid_only",
            kwargs={"pkid": self.published_panel.id},
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_panel_by_pkid(self):
        """Test that the panel ViewOne returns the correct panel."""
        url = reverse(
            "topicblog:view_panel_by_pkid",
            kwargs={"pkid": self.published_panel.id, "the_slug": "test-panel"},
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )
            if response.status_code == 200:
                self.assertContains(response, self.published_panel.title)

        # Test that the panel view returns 404 for a bad pkid.
        url = reverse(
            "topicblog:view_panel_by_pkid",
            kwargs={"pkid": 999999999, "the_slug": "test-panel"},
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_new_panel_get(self):
        """Test that the new_panel url is reachable."""
        url = reverse("topicblog:new_panel")

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

    def test_new_panel_post(self):
        """Test that new_panel url POST creates TBPanels."""
        url = reverse("topicblog:new_panel")

        form_data = {
            "slug": "test-panel-2",
            "title": "Test Panel Title (post)",
            "body_text_1_md": "**POST**",
            "template_name": "topicblog/panel_did_you_know_tip_1.html",
        }

        response = self.authorized_user_client.post(url, form_data)
        created_panel = TopicBlogPanel.objects.last()
        self.assertEqual(created_panel.title, form_data["title"])
        self.assertEqual(
            created_panel.body_text_1_md, form_data["body_text_1_md"]
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, created_panel.get_absolute_url())

        response = self.no_permissions_client.post(url, form_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("authentication:login") + "?next=" + url
        )

    def test_edit_panel_by_pkid_get(self):
        """Test that we can edit slugless panels."""
        url = reverse(
            "topicblog:edit_panel_by_pkid",
            kwargs={"pkid": self.slugless_panel.id},
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

        # Test that the panel view returns 404 for a bad pkid.
        url = reverse(
            "topicblog:edit_panel_by_pkid", kwargs={"pkid": 999999999}
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test that the panel view returns 40X for a panel with a slug
        # or redirects to login if not logged in.
        url = reverse(
            "topicblog:edit_panel_by_pkid",
            kwargs={"pkid": self.published_panel.id},
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.no_permissions_client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("authentication:login") + "?next=" + url
        )

    def test_edit_panel_by_pkid_post(self):
        url = reverse(
            "topicblog:edit_panel_by_pkid",
            kwargs={"pkid": self.slugless_panel.id},
        )

        form_data = {
            "title": "Test Panel Title slugless (post)",
            "body_text_1_md": "**POST**",
            "template_name": "topicblog/panel_did_you_know_tip_1.html",
        }

        response = self.authorized_user_client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, TopicBlogPanel.objects.last().get_absolute_url()
        )

        response = self.no_permissions_client.post(url, form_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("authentication:login") + "?next=" + url
        )

    def test_edit_panel_get(self):
        """Test edit_panel GET"""
        url = reverse(
            "topicblog:edit_panel",
            kwargs={"pkid": self.published_panel.id, "the_slug": "test-panel"},
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

        # Test that the panel view returns 404 for a bad pkid.
        url = reverse(
            "topicblog:edit_panel",
            kwargs={"pkid": 999999999, "the_slug": "test-panel"},
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

        # Test that the panel view returns 40X for a panel without a slug
        # or redirects to login if not logged in.
        url = reverse(
            "topicblog:edit_panel",
            kwargs={"pkid": self.slugless_panel.id, "the_slug": "test-panel"},
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 404)

        response = self.no_permissions_client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("authentication:login") + "?next=" + url
        )

    def test_edit_panel_post(self):
        """Test edit_panel POST"""
        url = reverse(
            "topicblog:edit_panel",
            kwargs={
                "pkid": self.published_panel.id,
                "the_slug": self.published_panel.slug,
            },
        )

        form_data = {
            "title": "Test Panel Title (post)",
            "body_text_1_md": "**POST (edit)**",
            "template_name": "topicblog/panel_did_you_know_tip_1.html",
            "body_image_1": self.uploaded_image,
            "body_image_1_alt_text": "Test Image Alt Text",
        }

        response = self.authorized_user_client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        last_panel = TopicBlogPanel.objects.last()
        self.assertEqual(response.url, last_panel.get_absolute_url())
        self.assertEqual(last_panel.title, form_data["title"])
        self.assertEqual(
            last_panel.body_text_1_md, form_data["body_text_1_md"]
        )
        self.assertEqual(last_panel.template_name, form_data["template_name"])
        # Because the uploaded image is converted from SimpleUploadedFile
        # to ImageField, the image name is different,
        # and class is also different. Best we can do to check image persistence
        # is to check that the image changed, and isn't None.
        self.assertNotEqual(last_panel.body_image_1, None)
        self.assertNotEqual(last_panel.body_image_1, self.image)

        response = self.no_permissions_client.post(url, form_data)
        self.assertEqual(response.status_code, 403)

        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("authentication:login") + "?next=" + url
        )

    def test_edit_panel_by_slug_get(self):
        """Test edit_panel_by_slug GET"""
        url = reverse(
            "topicblog:edit_panel_by_slug", kwargs={"the_slug": "test-panel"}
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

        # If a bad slug is provided, the form is equivalennt to a new panel
        url = reverse(
            "topicblog:edit_panel_by_slug", kwargs={"the_slug": "bad-slug"}
        )
        response = self.authorized_user_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_panel_get(self):
        """Test list_panel GET"""
        url = reverse("topicblog:list_panel")

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

    def test_list_panel_by_slug(self):
        """Test list_panel_by_slug GET"""
        url = reverse(
            "topicblog:list_panel_by_slug", kwargs={"the_slug": "test-panel"}
        )

        # Testing status codes for valid urls
        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(url)
            self.assertEqual(
                response.status_code, user_type["code"], user_type["msg"]
            )

        url = reverse(
            "topicblog:list_panel_by_slug", kwargs={"the_slug": "bad-slug"}
        )
        response = self.authorized_user_client.get(url)
        self.assertContains(response, "Aucun résultat.")
