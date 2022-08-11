from datetime import datetime, timezone, timedelta
from typing import List, TypedDict

from django.contrib.auth.models import Permission, User
from django.test import TestCase, Client
from django.urls import reverse
from mailing_list.models import MailingList

from topicblog.models import (EmailCampaign, SendRecordMarketingEmail,
                              SendRecordMarketingPress)


class DashboardTests(TestCase):

    def setUp(self) -> None:
        # Create a user
        self.noperms_user = User.objects.create_user(
            username='testuser',
            password="testpassword",
            email="noperms.user@example.com")
        self.authorized_user = User.objects.create_user(
            username='authorized_user',
            password="testpassword",
            email="authorized.user@example.com")
        # Add a permission
        tbe_send_permission = Permission.objects.get(
            codename='tbe.may_send')
        tbp_send_permission = Permission.objects.get(
            codename='tbp.may_send')
        see_dashboard = Permission.objects.get(
            codename='dashboard.may_see'
        )
        # Add permissions to users
        self.authorized_user.user_permissions.add(tbe_send_permission)
        self.authorized_user.user_permissions.add(tbp_send_permission)
        self.authorized_user.user_permissions.add(see_dashboard)
        self.authorized_user.save()
        # Create clients
        self.anon_client = Client()
        self.logged_in_client = Client()
        self.logged_in_client.force_login(self.noperms_user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.authorized_user)

        # Create lists of clients with their expected status code and error
        self.login_and_permissions_required = [
            {"client": self.logged_in_client, "code": 403,
             "msg": "No perms users don't have acces to this page"},
            {"client": self.anon_client, "code": 302,
             "msg": "Anon user don't have acces to this page"},
            {"client": self.authorized_client, "code": 200,
             "msg": "Auth user with permission have acces to this page"},
        ]
        self.login_required = [
            {"client": self.logged_in_client, "code": 200,
                "msg": "Logged in user have acces to this page"},
            {"client": self.anon_client, "code": 302,
                "msg": "Anon user don't have acces to this page"},
            {"client": self.authorized_client, "code": 200,
                "msg": "Auth user with permission have acces to this page"},
        ]
        # Create 2 mailing lists : Newsletter and Press
        self.newsletter_list = MailingList.objects.create(
            mailing_list_name="the_mailing_list_name",
            mailing_list_token="the_mailing_list_token",
            mailing_list_type="NEWSLETTER",
            list_active=True)
        self.press_list = MailingList.objects.create(
            mailing_list_name="the_mailing_list_name_2",
            mailing_list_token="the_mailing_list_token_2",
            mailing_list_type="PRESS",
            list_active=True)

        # Create email campaigns
        self.newsletter_campaign = EmailCampaign.objects.create(
            mailing_list=self.newsletter_list)
        self.press_campaign = EmailCampaign.objects.create(
            mailing_list=self.press_list)

        # Create send records associated with email campaigns
        self.default_date = datetime(2022, 8, 11, tzinfo=timezone.utc)
        send_records_email_to_create = [
            SendRecordMarketingEmail(
                slug='the-newsletter-slug',
                mailinglist=self.newsletter_list,
                email_campaign=self.newsletter_campaign,
                recipient=self.noperms_user,
                status="SENT",
                handoff_time=self.default_date,
                send_time=self.default_date + timedelta(seconds=2),
                open_time=self.default_date + timedelta(hours=3),
            ),
            SendRecordMarketingEmail(
                slug='the-newsletter-slug',
                mailinglist=self.newsletter_list,
                email_campaign=self.newsletter_campaign,
                recipient=self.authorized_user,
                status="SENT",
                handoff_time=self.default_date,
                send_time=self.default_date + timedelta(seconds=3),
                open_time=self.default_date + timedelta(hours=4),
            )
        ]
        send_records_press_to_create = [
            SendRecordMarketingPress(
                slug='the-press-slug',
                mailinglist=self.press_list,
                email_campaign=self.press_campaign,
                recipient=self.noperms_user,
                status="SENT",
                handoff_time=self.default_date,
                send_time=self.default_date + timedelta(seconds=2),
                open_time=self.default_date + timedelta(hours=3),
            ),
            SendRecordMarketingPress(
                slug='the-press-slug',
                mailinglist=self.press_list,
                email_campaign=self.press_campaign,
                recipient=self.authorized_user,
                status="SENT",
                handoff_time=self.default_date,
                send_time=self.default_date + timedelta(seconds=3),
                open_time=None,
            )
        ]
        SendRecordMarketingEmail.objects.bulk_create(send_records_email_to_create)
        SendRecordMarketingPress.objects.bulk_create(send_records_press_to_create)

    class ClientDict(TypedDict):
        """Dict of client, code and error messages
        Strictly used for type hinting.
        """
        client: Client
        code: int
        msg: str

    def _test_access_policy(self, clients: List[ClientDict], url: str):
        """Test access policy for a given url

        Keyword arguments:
        clients -- list of clients to test, contains dict with client,
        expected response code, and error message.
        url -- url to test.
        """
        for client_type in clients:
            response = client_type["client"].get(url)
            self.assertEqual(
                response.status_code,
                client_type["code"],
                msg=client_type["msg"])

    def test_status_codes(self):
        """Test status codes for all urls"""
        login_and_permissions_required_urls = [
            reverse("dashboard:index"),
            reverse("dashboard:email_campaigns"),
            reverse("dashboard:email_campaign_details", kwargs={"pk": 1}),
            reverse("dashboard:user_send_records", kwargs={"pk": 1}),
        ]
        login_required_urls = [
            reverse("dashboard:signature"),
        ]
        for url in login_required_urls:
            self._test_access_policy(
                self.login_required, url)

        for url in login_and_permissions_required_urls:
            self._test_access_policy(
                self.login_and_permissions_required, url)

    def test_search_by_email(self):
        """Test search by email"""
        url = reverse("dashboard:email_campaigns")
        response = self.authorized_client.post(
            url, {"email": self.authorized_user.email})
        self.assertRedirects(
            response,
            expected_url=reverse("dashboard:user_send_records",
                                 kwargs={"pk": self.authorized_user.pk}),
            status_code=302,
            target_status_code=200,
        )
        response = self.authorized_client.post(
            url,
            {"email": "not-an-email"}
        )
        self.assertEqual(response.status_code, 200)
        # Check that a message is present
        self.assertContains(
            response,
            "Aucun utilisateur ne correspond à cette adresse.",
        )
