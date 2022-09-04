from unittest.mock import patch
from django.test import TestCase, Client
from .models import PressMention
from datetime import datetime, timezone
from django.contrib.auth.models import User, Permission
from django.urls import reverse


class PressMentionTestCase(TestCase):
    def setUp(self):
        # Create two Pressmention object
        self.journal_report = PressMention.objects.create(
            newspaper_name="journal",
            article_link="https://www.example.com/article/1",
            article_title="titre",
            article_summary="description",
            article_publication_date=datetime.now(timezone.utc),
            og_title="og title",
            og_description="og description",
            og_image="image.png",
        )
        self.journal_report_1 = PressMention.objects.create(
            newspaper_name="journal 1",
            article_link="https://www.example.com/article/2",
            article_title="titre 1",
            article_summary="description 1",
            article_publication_date=datetime.now(timezone.utc),
            og_title="og title 1",
            og_description="og description 1",
            og_image="image1.png",
        )
        self.user = User.objects.create_user(username='user',
                                             password='password')
        self.user.save()
        # Create a user with editor press permission
        self.user_permited = User.objects.create_user(username='press-staff',
                                                      password='press-staff')
        editor_press = Permission.objects.get(codename="press-editor")
        self.user_permited.user_permissions.add(editor_press)
        self.user_permited.save()

        # Create the client for the users
        self.user_permited_client = Client()
        self.unauth_client = Client()

        # login the users
        self.client.login(username='user', password='password')
        self.user_permited_client.login(
            username='press-staff', password='press-staff')

        # Create a user
    def test_model_str_function(self):
        self.assertEqual(self.journal_report.__str__(), "journal titre",
                         msg="Should return the newspaper name"
                             " a space and the title of the article")
        self.assertEqual(self.journal_report_1.__str__(), "journal 1 titre 1",
                         msg="Should return the newspaper name"
                         " a space and the title of the article")

    def test_view_press(self):
        """All user should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected = [
            {"client": self.client, "code": 200,
             "msg": "Auth user have access to view"},
            {"client": self.unauth_client, "code": 200,
             "msg": "Unauth user have access to view"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to view"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(reverse("press:view"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_list_view_press(self):
        """Only user with press-editor permission should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to list view"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to list view"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(reverse("press:list_items"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # Testing list view newpapers filter
        users_expected_1 = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to list view"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to list view"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(f"{reverse('press:list_items')}"
                                               "?newspaper_name=journal")
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_create_view_press(self):
        """Only user with press-editor permission should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to create view."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to create view"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(reverse("press:new_item"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_update_view_press(self):
        """Only user with press-editor permission should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to update view."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to update view"},
        ]
        for user_type in users_expected:
            response = \
                user_type["client"].get(reverse(
                    "press:update_item",
                    kwargs={
                        "pk": self.journal_report.id,
                    }))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_delete_view_press(self):
        """Only user with press-editor permission should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to update view."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to update view"},
        ]
        for user_type in users_expected:
            response = \
                user_type["client"].get(reverse(
                    "press:delete_item",
                    kwargs={
                        "pk": self.journal_report.id,
                    }))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    @patch("requests.get")
    def test_post_new_press_mention(self, mock_request):
        og_title = "Test title"
        og_description = "Test description"
        og_image = "https://example.com/test.jpg"
        mock_request.return_value.status_code = 200
        mock_request.return_value.content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                <meta property="og:title" content="{og_title}" />
                <meta property="og:description" content="{og_description}" />
                <meta property="og:image" content="{og_image}" />
                </head>
            </html>
        """.encode("utf-8")
        complete_url = "http://example.com/"
        self.user_permited_client.post(
            reverse("press:new_item"),
            {'newspaper_name': 'test_post', 'article_link': complete_url,
             'article_title': 'test', 'article_summary': 'mini sum',
             'article_publication_date': '2022-03-31'})
        new_press_mention = PressMention.objects.filter(
            newspaper_name__iexact="test_post").get()
        self.assertEqual(new_press_mention.og_title, og_title)
        self.assertEqual(new_press_mention.og_description, og_description)
        # # As long as we're fetching a non-existent image, we'll
        # # fail to determine a file type.
        # self.assertIn(".jpeg", new_press_mention.og_image.url)

    def test_detail_view_press(self):
        """Only user with press-editor permission should have access to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the excepted statut code
            - message = the error message"""
        users_expected = [
            {"client": self.client, "code": 403,
             "msg": "Auth user without permission can't access to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user have access to create view."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have access to create view"},
        ]
        for user_type in users_expected:
            response = \
                user_type["client"].get(reverse(
                    "press:detail_item",
                    kwargs={
                        "pk": self.journal_report.id,
                    }))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
