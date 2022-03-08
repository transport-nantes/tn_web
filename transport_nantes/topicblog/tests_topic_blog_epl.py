from datetime import datetime, timezone
from django.test import TestCase, Client
from .models import TopicBlogEmail, TopicBlogPress
from django.contrib.auth.models import Permission, User
from django.urls import reverse


class TBETest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        self.user.save()
        # Create a user with all permission
        self.staff = User.objects.create_superuser(username='test-staff',
                                                   password='test-staff')
        edit_permission = Permission.objects.get(codename="tbe.may_edit")
        view_permission = Permission.objects.get(codename="tbe.may_view")
        publish_permission = Permission.objects.get(codename="tbe.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbe.may_publish_self")
        self.staff.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission
        )
        self.staff.save()
        # Create client and log user into the client
        self.user_client = Client()
        self.staff_client = Client()

        self.user_client.login(username='test-user', password='test-pass')
        self.staff_client.login(username='test-staff', password='test-staff')

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
            title="Test-title")

        self.email_without_slug = TopicBlogEmail.objects.create(
            subject="subject2",
            body_text_1_md="body2",
            user=self.staff,
            template_name=self.template_email,
            title="Test-title")

    """ TESTING MODEL"""

    def test_str_func(self):
        good_str_with_slug = (f"{self.email_with_slug.slug} - "
                              f"{self.email_with_slug.title} - "
                              f"ID : {self.email_with_slug.id}")
        self.assertEqual(self.email_with_slug.__str__(), good_str_with_slug)
        good_str_without_slug = (f"{self.email_without_slug.title} - "
                                 f"ID : {self.email_without_slug.id} "
                                 "(NO SLUG)")
        self.assertEqual(
            self.email_without_slug.__str__(), good_str_without_slug)

    """ TESTING VIEW """

    def test_view_by_slug(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good slug
        users_expected_0 = [
            {"client": self.user_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
            {"client": self.client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_slug",
                        kwargs={
                            "the_slug": self.email_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # with bad slug
        users_expected_1 = [
            {"client": self.user_client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
            {"client": self.client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_slug",
                        kwargs={
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_view_email_by_pkid_only(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the"
             " good pkid but the item have a slug"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid_only",
                        kwargs={
                            "pkid": self.email_with_slug.id,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with good pkid but item don't have slug
        users_expected_1 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the"
             " good pkid and the item don't have slug"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid_only",
                        kwargs={
                            "pkid": self.email_without_slug.id,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with bad pkid
        users_expected_2 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we don't provide"
             " a good pkid"},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid_only",
                        kwargs={
                            "pkid": 999999999,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_view_email_by_pkid(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the"
             " good pkid and the good slug"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid",
                        kwargs={
                            "pkid": self.email_with_slug.id,
                            "the_slug": self.email_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with good pkid bad slug
        users_expected_1 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the"
             " good pkid and and the wrong slug"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid",
                        kwargs={
                            "pkid": self.email_with_slug.id,
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with bad pkid and good slug
        users_expected_2 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we don't provide"
             " a good pkid"},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:view_email_by_pkid",
                        kwargs={
                            "pkid": 999999999,
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_new_email(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if user have the"
             " have the permission"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:new_email")
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_list_emails(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide no parameters."},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_emails")
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_list_items_by_slug(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide no parameters."},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_emails_by_slug",
                        kwargs={
                            "the_slug": self.email_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])


class TBPTest(TestCase):
    def setUp(self):

        TBETest.setUp(self)
        edit_permission = Permission.objects.get(codename="tbp.may_edit")
        view_permission = Permission.objects.get(codename="tbp.may_view")
        publish_permission = Permission.objects.get(codename="tbp.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbp.may_publish_self")
        self.staff.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission
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
            title="Test-title")
        self.press_without_slug = TopicBlogPress.objects.create(
            subject="subject1",
            body_text_1_md="body1",
            user=self.staff,
            template_name=self.template_press,
            title="Test-title")

    """ TESTING MODEL"""

    def test_str_func(self):
        good_str_with_slug = (f"{self.press_with_slug.slug} - "
                              f"{self.press_with_slug.title} - "
                              f"ID : {self.press_with_slug.id}")
        self.assertEqual(self.press_with_slug.__str__(), good_str_with_slug)
        good_str_without_slug = (f"{self.press_without_slug.title} - "
                                 f"ID : {self.press_without_slug.id} "
                                 "(NO SLUG)")
        self.assertEqual(
            self.press_without_slug.__str__(), good_str_without_slug)

    """ TESTING VIEW """

    def test_view_by_slug(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good slug
        users_expected_0 = [
            {"client": self.user_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
            {"client": self.client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the the good"
             " slug and the topicblog is publied"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_slug",
                        kwargs={
                            "the_slug": self.press_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # with bad slug
        users_expected_1 = [
            {"client": self.user_client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
            {"client": self.client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we provide a "
             "wrong slug not related to any item."},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_slug",
                        kwargs={
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_view_press_by_pkid_only(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good pkid but item have a slug
        users_expected_0 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the"
             " good pkid but the item have a slug"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid_only",
                        kwargs={
                            "pkid": self.press_with_slug.id,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with good pkid but item don't have slug
        users_expected_1 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the"
             " good pkid and the item don't have slug"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid_only",
                        kwargs={
                            "pkid": self.press_without_slug.id,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with bad pkid
        users_expected_2 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we don't provide"
             " a good pkid"},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid_only",
                        kwargs={
                            "pkid": 999999999,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_view_press_by_pkid(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        # with good pkid and good slug
        users_expected_0 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the"
             " good pkid and the good slug"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid",
                        kwargs={
                            "pkid": self.press_with_slug.id,
                            "the_slug": self.press_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with good pkid bad slug
        users_expected_1 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the"
             " good pkid and and the wrong slug"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid",
                        kwargs={
                            "pkid": self.press_with_slug.id,
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # with bad pkid and good slug
        users_expected_2 = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 404,
             "msg": "The page should return 404 if we don't provide"
             " a good pkid"},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:view_press_by_pkid",
                        kwargs={
                            "pkid": 999999999,
                            "the_slug": "bad-slug",
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_new_press(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if user have the"
             " have the permission"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:new_press")
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_list_presss(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide no parameters."},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_press")
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_list_items_by_slug(self):
        """"For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)"""

        users_expected = [
            {"client": self.user_client, "code": 403,
             "msg": "Normal users can't access this page."},
            {"client": self.client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.staff_client, "code": 200,
             "msg": "The page MUST return 200 if we provide no parameters."},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("topicblog:list_press_by_slug",
                        kwargs={
                            "the_slug": self.press_with_slug.slug,
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
