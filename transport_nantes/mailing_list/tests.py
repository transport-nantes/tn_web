from django.test import TestCase, LiveServerTestCase, Client
from .models import MailingList, MailingListEvent, Petition
from datetime import datetime, timezone
from django.contrib.auth.models import User, Permission
from django.contrib.auth.models import User
from topicblog.models import TopicBlogItem
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from django.urls import reverse
from .events import user_current_state


class MailingListTestCase(TestCase):
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
        # Create a user
        self.user = User.objects.create_user(username='user',
                                             password='password',
                                             email="user@nomail.fr"
                                             )
        self.user.save()
        # Create a user with editor historic mail event permission
        self.user_permited = User.objects.create_user(username='ml-staff',
                                                      password='ml-staff',
                                                      email="staff@nomail.fr")

        # mailing_permission =
        # Permission.objects.get(codename="pii_authorised")
        # self.user_permited.user_permissions.add(mailing_permission)
        # self.user_permited.save()

        # Create the client for the users
        self.user_permited_client = Client()
        self.unauth_client = Client()

        # login the users
        self.client.login(username='user', password='password')
        self.user_permited_client.login(
            username='ml-staff', password='ml-staff')

        # Create MailingListEvent object
        self.mailing_event_1 = MailingListEvent.objects.create(
            user=self.user, mailing_list=self.mailing_list_1,
            event_type=MailingListEvent.EventType.SUBSCRIBE)

        self.mailing_event_2 = MailingListEvent.objects.create(
            user=self.user_permited, mailing_list=self.mailing_list_3,
            event_type=MailingListEvent.EventType.SUBSCRIBE)

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
                         ("U=  <user@nomail.fr> (), L=news1 (token1)"
                             " f=0 semaines, E=sub, "
                             f"{self.mailing_event_1.event_timestamp}"),
                         msg="Should return the the data :"
                             "U={u_fn} {u_ln} <{u_e}> ({u_commune}),"
                             " L={mlist}, E={event}, {ts}")
        self.assertEqual(self.mailing_event_2.__str__(),
                         ("U=  <staff@nomail.fr> (), L=petition1 (token3)"
                             " f=0 semaines, E=sub, "
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
            {"client": self.client, "code": 200,
             "msg": "Auth user have acces to this page"},
            {"client": self.unauth_client, "code": 302,
             "msg": "Unauth user don't have acces to this page"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "Auth user with permission have acces to this page"},
        ]
        for user_type in users_expected:
            response = user_type["client"].get(
                reverse("mailing_list:user_status"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_status_page_context(self):
        # testing user without perm
        response_0 = self.client.get(reverse("mailing_list:user_status"))
        good_mailing_list_0 = list()
        good_petition_list_0 = list()
        base_lists = MailingList.objects.filter(
            list_active=True).order_by(
                'is_petition', 'mailing_list_name')
        for mailing_list in base_lists:
            state = user_current_state(
                self.user, mailing_list).event_type
            if not mailing_list.is_petition:
                good_mailing_list_0.append((mailing_list, state,))
            else:
                good_petition_list_0.append((mailing_list, state,))
        self.assertListEqual(response_0.context['mailing_lists'],
                             good_mailing_list_0)
        self.assertListEqual(response_0.context['petitions_lists'],
                             good_petition_list_0)
        # testing user with perm
        response_1 = self.user_permited_client.get(
            reverse("mailing_list:user_status"))
        good_mailing_list_1 = list()
        good_petition_list_1 = list()
        base_lists = MailingList.objects.filter(
            list_active=True).order_by(
                'is_petition', 'mailing_list_name')
        for mailing_list in base_lists:
            state = user_current_state(
                self.user_permited, mailing_list).event_type
            if not mailing_list.is_petition:
                good_mailing_list_1.append((mailing_list, state,))
            else:
                good_petition_list_1.append((mailing_list, state,))
        self.assertListEqual(response_1.context['mailing_lists'],
                             good_mailing_list_1)
        self.assertListEqual(response_1.context['petitions_lists'],
                             good_petition_list_1)
        # Testing that both context is not the same
        self.assertNotEqual(good_mailing_list_0, good_mailing_list_1)
        self.assertNotEqual(good_petition_list_0, good_petition_list_1)


class MailingListIntegrationTestCase(LiveServerTestCase):
    def setUp(self):
        # Create a topicblog page for testing quick sign up
        MailingListTestCase.setUp(self)
        self.home = TopicBlogItem.objects.create(
            slug="home",
            date_modified=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.user_permited,
            template_name="topicblog/content.html",
            title="home-title")
        # Create the default mailing list
        self.mailing_list_default = MailingList.objects.create(
            mailing_list_name="general-quarterly",
            mailing_list_token="general-quarterly",
            contact_frequency_weeks=1,
            list_active=True,
        )
        self.cookie_user = self.client.cookies['sessionid'].value
        self.cookie_staff = \
            self.user_permited_client.cookies['sessionid'].value
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.selenium = WebDriver(ChromeDriverManager().install(),
                                  options=options)
        self.selenium.implicitly_wait(5)

    def tearDown(self):
        # Close the browser
        self.selenium.quit()

    def testing_user_status_page_subscribe_to_newsletter(self):
        old_event = user_current_state(self.user, self.mailing_list_2)
        self.assertEqual(old_event.event_type, "unsub")
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("mailing_list:user_status")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_user,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("mailing_list:user_status")))
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
                         msg="The event is not update")
        self.assertEqual(a_html, "Se désabonner", msg="The page is not update")

    def testing_user_status_page_unsubscribe_to_newsletter(self):
        old_event = user_current_state(self.user, self.mailing_list_1)
        self.assertEqual(old_event.event_type, "sub")
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("mailing_list:user_status")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_user,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("mailing_list:user_status")))
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
                         msg="The event is not update")
        self.assertEqual(button_html, "S'abonner",
                         msg="The page is not update")

    def testing_quick_form(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("topicblog:view_item_by_slug",
                                            kwargs={
                                                "the_slug": self.home.slug
                                            })))
        email_input = self.selenium.find_element_by_id("id_email")
        email_input.send_keys("nomail@nomail.fr")
        self.selenium.find_element_by_css_selector(
            "form button[type=submit]").click()
        # pass the captcha only work on dev mod
        captcha_input = self.selenium.find_element_by_id("id_captcha_1")
        captcha_input.send_keys("PASSED")
        self.selenium.find_element_by_css_selector(
            "form button[type=submit]").click()
        user = User.objects.filter(email="nomail@nomail.fr")[0]
        self.assertIsNotNone(user,
                             msg="The user is not created on quick sign up")
        mailing_list_event = MailingListEvent.objects.filter(user=user)[0]
        self.assertIsNotNone(mailing_list_event,
                             msg="The mailing event is not created"
                                 "on quick sign up")

        self.assertEqual(mailing_list_event.event_type, "sub",
                         msg="The user is not sub on the default mailing list")
