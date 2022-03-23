from django.test import Client, LiveServerTestCase, TestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from topicblog.models import TopicBlogItem
from datetime import datetime, timezone
from .models import MailingList, MailingListEvent, Petition
from django.contrib.auth.models import User
from django.urls import reverse
from .events import user_current_state


class MailingListIntegrationTestCase(LiveServerTestCase):
    def setUp(self):
        # Create MailingList (newsletter) object
        self.mailing_list_1 = MailingList.objects.create(
            mailing_list_name="news1",
            mailing_list_token="token1",
            list_active=True,
        )
        self.mailing_list_2 = MailingList.objects.create(
            mailing_list_name="news2",
            mailing_list_token="token2",
            contact_frequency_weeks=4,
            list_active=True,
        )
        # Create MailingList (petition) object
        self.mailing_list_3 = MailingList.objects.create(
            mailing_list_name="petition1",
            mailing_list_token="token3",
            list_active=True,
            is_petition=True,
        )
        self.mailing_list_4 = MailingList.objects.create(
            mailing_list_name="petition2",
            mailing_list_token="token4",
            list_active=True,
            is_petition=True,
        )
        # Create two Petition (petition) object
        self.petition_1 = Petition.objects.create(
            mailing_list=self.mailing_list_3,
            slug="slug1",
            petition1_md="First sentence",
        )
        self.petition_2 = Petition.objects.create(
            mailing_list=self.mailing_list_4,
            slug="slug2",
            petition1_md="First sentence 2",
        )
        self.user = User.objects.create_user(username='ml-staff',
                                             password='ml-staff',
                                             email="staff@example.com")
        self.user.save()
        self.logged_client = Client()
        self.logged_client.login(username='ml-staff', password='ml-staff')
        self.superuser = \
            User.objects.create_superuser(username='ml-admin',
                                          password='ml-admin',
                                          email="admin@example.com")
        self.superuser.save()
        self.admin_client = Client()
        self.admin_client.login(username='ml-admin', password='ml-admin')
        # Create a topicblog page for testing quick sign up
        self.home = TopicBlogItem.objects.create(
            slug="home",
            date_modified=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.superuser,
            template_name="topicblog/content.html",
            title="home-title")
        # Create the default mailing list
        self.mailing_list_default = MailingList.objects.create(
            mailing_list_name="general-quarterly",
            mailing_list_token="general-quarterly",
            contact_frequency_weeks=12,
            list_active=True,
        )
        # Create MailingListEvent object
        self.mailing_event_1 = MailingListEvent.objects.create(
            user=self.user, mailing_list=self.mailing_list_1,
            event_type=MailingListEvent.EventType.SUBSCRIBE)

        self.mailing_event_2 = MailingListEvent.objects.create(
            user=self.superuser, mailing_list=self.mailing_list_2,
            event_type=MailingListEvent.EventType.SUBSCRIBE)

        self.cookie_user = self.logged_client.cookies['sessionid'].value
        self.cookie_staff = \
            self.admin_client.cookies['sessionid'].value

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.selenium = WebDriver(ChromeDriverManager().install(),
                                  options=options)
        self.selenium.implicitly_wait(5)

    def tearDown(self):
        # Close the browser
        self.selenium.quit()

    # def testing_quick_form_logged_out(self):
    #     self.selenium.get('%s%s' % (self.live_server_url,
    #                                 reverse("topicblog:view_item_by_slug",
    #                                         kwargs={
    #                                             "the_slug": self.home.slug
    #                                         })))
    #     email_input = self.selenium.find_element_by_id("id_email")
    #     email_input.send_keys("nomail@nomail.fr")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     # pass the captcha only work on dev mod
    #     captcha_input = self.selenium.find_element_by_id("id_captcha_1")
    #     captcha_input.send_keys("PASSED")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     user = User.objects.filter(email="nomail@nomail.fr").first()
    #     self.assertIsNotNone(
    #         user,
    #         msg="The user was not created during mailing list signup")
    #     mailing_list_event = MailingListEvent.objects.filter(user=user).first()
    #     self.assertIsNotNone(mailing_list_event,
    #                          msg="The mailing event is not created"
    #                              "on quick sign up")

    #     self.assertEqual(
    #         mailing_list_event.event_type, "sub",
    #         msg="The user is not subscribed to the default mailing list")

    def testing_quick_form_logged_in(self):
        # Get on mobilitains website
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("topicblog:view_item_by_slug",
                                            kwargs={
                                                "the_slug": self.home.slug
                                            })))
        # Add a session cookie to the browser (refused if not already on the
        # website)
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_user,
             'secure': False, 'path': '/'})
        # Refresh the page to get the proper display
        self.selenium.refresh()
        # because we're already logged in, we're subbed to the default
        # list without captcha
        self.selenium.find_element_by_css_selector(
            "form button[type=submit]").click()
        # We wait until next page is loaded (confirmation page)
        WebDriverWait(self.selenium, 5).until(
            EC.url_contains(reverse("mailing_list:quick_signup"))
        )
        # We used the self.user's cookie to connect to the website
        user = User.objects.filter(email=self.user.email).first()
        self.assertIsNotNone(
            user,
            msg="The user created during setUp does not exist")
        mailing_list_event = MailingListEvent.objects.filter(user=user).first()
        self.assertIsNotNone(mailing_list_event,
                             msg="The mailing event was not created "
                                 "on quick sign up")

        self.assertEqual(mailing_list_event.event_type, "sub",
                         msg="The user is not sub on the default mailing list")

    # def testing_quick_form_fail_captcha_logged_out(self):
    #     self.selenium.get('%s%s' % (self.live_server_url,
    #                                 reverse("topicblog:view_item_by_slug",
    #                                         kwargs={
    #                                             "the_slug": self.home.slug
    #                                         })))
    #     email_input = self.selenium.find_element_by_id("id_email")
    #     email_input.send_keys("nomail@nomail.fr")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     # fail the capcha
    #     captcha_input = self.selenium.find_element_by_id("id_captcha_1")
    #     captcha_input.send_keys("Notgood")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     # pass the captcha only work on dev mod
    #     captcha_input = self.selenium.find_element_by_id("id_captcha_1")
    #     captcha_input.send_keys("PASSED")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     user = User.objects.filter(email="nomail@nomail.fr").first()
    #     self.assertIsNotNone(user,
    #                          msg="The user is not created on quick sign up")
    #     mailing_list_event = MailingListEvent.objects.filter(user=user).first()
    #     self.assertIsNotNone(mailing_list_event,
    #                          msg="The mailing event is not created"
    #                              "on quick sign up")

    #     self.assertEqual(mailing_list_event.event_type, "sub",
    #                      msg="The user is not sub on the default mailing list")

    # def testing_quick_form_fail_captcha_logged_in(self):
    #     self.selenium.get('%s%s' % (self.live_server_url,
    #                                 reverse("topicblog:view_item_by_slug",
    #                                         kwargs={
    #                                             "the_slug": self.home.slug
    #                                         })))
    #     email_input = self.selenium.find_element_by_id("id_email")
    #     email_input.send_keys("nomail@nomail.fr")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     # fail the capcha
    #     captcha_input = self.selenium.find_element_by_id("id_captcha_1")
    #     captcha_input.send_keys("Notgood")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     # pass the captcha only work on dev mod
    #     captcha_input = self.selenium.find_element_by_id("id_captcha_1")
    #     captcha_input.send_keys("PASSED")
    #     self.selenium.find_element_by_css_selector(
    #         "form button[type=submit]").click()
    #     user = User.objects.filter(email="nomail@nomail.fr").first()
    #     self.assertIsNotNone(user,
    #                          msg="The user is not created on quick sign up")
    #     mailing_list_event = MailingListEvent.objects.filter(user=user).first()
    #     self.assertIsNotNone(mailing_list_event,
    #                          msg="The mailing event is not created"
    #                              "on quick sign up")

    #     self.assertEqual(mailing_list_event.event_type, "sub",
    #                      msg="The user is not sub on the default mailing list")

    def testing_acces_with_get_to_the_quick_form(self):
        quick_signup_url = reverse("mailing_list:quick_signup")
        self.selenium.get(f"{self.live_server_url}{quick_signup_url}")
        index_url = f"{self.live_server_url}{reverse('index')}#newsletter"
        self.assertEqual(self.selenium.current_url, index_url,
                         msg="User SHOULD be redirect to index page")

    def testing_user_status_page_subscribe_to_newsletter(self):
        old_event = user_current_state(self.user, self.mailing_list_2)
        self.assertEqual(old_event.event_type, "unsub")
        user_status_url = reverse("mailing_list:user_status")
        self.selenium.get(f"{self.live_server_url}{user_status_url}")
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_user,
             'secure': False, 'path': '/'})
        self.selenium.get(f"{self.live_server_url}{user_status_url}")
        self.selenium.find_element_by_css_selector(
            f"#id-ml-{self.mailing_list_2.id} form button[type=submit]"
        ).click()
        a_html = \
            self.selenium.find_element_by_css_selector(
                f"#id-ml-{self.mailing_list_2.id} div a").get_attribute(
                    'innerHTML')
        new_event = user_current_state(self.user, self.mailing_list_2)
        # Check if the event is updated
        self.assertEqual(new_event.event_type, "sub",
                         msg="The event was not updated")
        self.assertEqual(a_html, "Se désabonner",
                         msg="The page is not updated")

    def testing_user_status_page_unsubscribe_to_newsletter(self):
        old_event = user_current_state(self.user, self.mailing_list_1)
        self.assertEqual(old_event.event_type, "sub")
        user_status_url = reverse("mailing_list:user_status")
        self.selenium.get(f"{self.live_server_url}{user_status_url}")
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_user,
             'secure': False, 'path': '/'})
        self.selenium.get(f"{self.live_server_url}{user_status_url}")
        self.selenium.find_element_by_css_selector(
            f"#id-ml-{self.mailing_list_1.id} a").click()
        self.selenium.find_element_by_css_selector(
            "form button[type=submit]").click()
        button_html = self.selenium.find_element_by_css_selector(
            f"#id-ml-{self.mailing_list_1.id} div button").get_attribute(
                'innerHTML')
        new_event = user_current_state(self.user, self.mailing_list_2)
        # Check if the event is updated
        self.assertEqual(new_event.event_type, "unsub",
                         msg="The event was not updated")
        self.assertEqual(button_html, "S'abonner",
                         msg="The page was not updated")


class MailingListStatusCodeTest(TestCase):
    def setUp(self):
        MailingListIntegrationTestCase.setUp(self)

    def test_mailing_list_list_signup(self):
        url = reverse("mailing_list:list_signup")
        response = self.logged_client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_quick_signup(self):
        url = reverse("mailing_list:quick_signup")
        # We expect a redirect on GETs if no mailing_list_token is provided
        response = self.logged_client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_quick_signup_with_mailing_list_token(self):
        url = reverse("mailing_list:quick_signup") + \
            f'?mailinglist={self.mailing_list_default.mailing_list_token}'

        # We expect a redirect on GETs if no mailing_list_token is provided
        response = self.logged_client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_quick_petition_signup(self):
        url = reverse("mailing_list:quick_petition_signup")
        response = self.logged_client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_items(self):
        url = reverse("mailing_list:list_items")
        response = self.logged_client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mailing_list_model_str_function(self):
        self.assertEqual(self.mailing_list_1.__str__(),
                         "news1 (token1) f=0 semaines",
                         msg="Should return the the data :"
                             " name (token) f=frequency semaines")
        self.assertEqual(self.mailing_list_2.__str__(),
                         "news2 (token2) f=4 semaines",
                         msg="Should return the the data :"
                             " name (token) f=frequency semaines")

    def test_petition_model_str_function(self):
        self.assertEqual(self.petition_1.__str__(),
                         "slug1  ->  (petition1)",
                         msg="Should return the the data :"
                             " slug  ->  (list_name)")
        self.assertEqual(self.petition_2.__str__(),
                         "slug2  ->  (petition2)",
                         msg="Should return the the data :"
                             " slug  ->  (list_name)")

    def test_mailing_list_event_model_str_function(self):
        self.assertEqual(self.mailing_event_1.__str__(),
                         ("U=  <staff@example.com> (), L=news1 (token1)"
                             " f=0 semaines, E=sub, "
                             f"{self.mailing_event_1.event_timestamp}"),
                         msg="Should return the the data :"
                             "U={u_fn} {u_ln} <{u_e}> ({u_commune}),"
                             " L={mlist}, E={event}, {ts}")
        self.assertEqual(self.mailing_event_2.__str__(),
                         ("U=  <admin@example.com> (), L=news2 (token2)"
                             " f=4 semaines, E=sub, "
                             f"{self.mailing_event_2.event_timestamp}"),
                         msg="Should return the the data :"
                             "U={u_fn} {u_ln} <{u_e}> ({u_commune}),"
                             " L={mlist}, E={event}, {ts}")

    def test_status_page_accessibility(self):
        """Only auth user have acces to this page
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the statut code excepted
            - message = the error message"""
        users_expected = [
            {"client": self.logged_client, "code": 200,
             "msg": "Auth user have acces to this page"},
            {"client": self.client, "code": 302,
             "msg": "Unauth user don't have acces to this page"},
            {"client": self.admin_client, "code": 200,
             "msg": "Auth user with permission have acces to this page"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("mailing_list:user_status"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_mailing_list_toggle_subscription_without_mailinglist(self):
        """All user have to be redirected
            For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and permited user)
            - code = the statut code excepted
            - message = the error message"""
        users_expected = [
            {"client": self.logged_client, "code": 302,
             "msg": "Auth user should be redirected"},
            {"client": self.client, "code": 302,
             "msg": "Unauth should be redirected to auth"},
            {"client": self.admin_client, "code": 302,
             "msg": "Auth user should be redirected"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("mailing_list:toggle_subscription"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_status_page_context(self):
        # testing user without perm
        response_0 = \
            self.logged_client.get(reverse("mailing_list:user_status"))
        good_mailing_list_0 = list()
        base_lists = MailingList.objects.filter(
            list_active=True).order_by(
                'is_petition', 'mailing_list_name')
        for mailing_list in base_lists:
            state = user_current_state(
                self.user, mailing_list).event_type
            if not mailing_list.is_petition:
                good_mailing_list_0.append((mailing_list, state,))
        self.assertListEqual(response_0.context['mailing_lists'],
                             good_mailing_list_0)
        # testing user with perm
        response_1 = \
            self.admin_client.get(reverse("mailing_list:user_status"))
        good_mailing_list_1 = list()
        base_lists = MailingList.objects.filter(
            list_active=True).order_by(
                'is_petition', 'mailing_list_name')
        for mailing_list in base_lists:
            state = user_current_state(
                self.superuser, mailing_list).event_type
            if not mailing_list.is_petition:
                good_mailing_list_1.append((mailing_list, state,))
        self.assertListEqual(response_1.context['mailing_lists'],
                             good_mailing_list_1)
        # Testing that both context is not the same
        self.assertNotEqual(good_mailing_list_0, good_mailing_list_1)
