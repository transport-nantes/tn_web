from django.test import LiveServerTestCase
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from topicblog.models import TopicBlogItem
from datetime import datetime, timezone
from .models import MailingList, MailingListEvent
from django.contrib.auth.models import User
from django.urls import reverse


class MailingListIntegrationTestCase(LiveServerTestCase):
    def setUp(self):
        self.user_permited = User.objects.create_user(username='ml-staff',
                                                      password='ml-staff',
                                                      email="staff@nomail.fr")
        # Create a topicblog page for testing quick sign up
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

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.selenium = WebDriver(ChromeDriverManager().install(),
                                  options=options)
        self.selenium.implicitly_wait(5)

    def tearDown(self):
        # Close the browser
        self.selenium.quit()

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

    def testing_quick_form_fail_captcha(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("topicblog:view_item_by_slug",
                                            kwargs={
                                                "the_slug": self.home.slug
                                            })))
        email_input = self.selenium.find_element_by_id("id_email")
        email_input.send_keys("nomail@nomail.fr")
        self.selenium.find_element_by_css_selector(
            "form button[type=submit]").click()
        # fail the capcha
        captcha_input = self.selenium.find_element_by_id("id_captcha_1")
        captcha_input.send_keys("Notgood")
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

    def testing_acces_with_get_to_the_quick_form(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    reverse("mailing_list:quick_signup")))
        index_url = f"{self.live_server_url}{reverse('index')}#newsletter"
        self.assertEqual(self.selenium.current_url, index_url,
                         msg="User should be redirect to index page")
