from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import Client, LiveServerTestCase, TestCase
from django.urls import reverse
from mailing_list.events import (get_subcribed_users_email_list,
                                 subscribe_user_to_list)
from mailing_list.models import MailingList
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .models import TopicBlogEmail, TopicBlogItem


class TestsTopicItemForm(LiveServerTestCase):

    def setUp(self):
        # all permission
        edit_permission = Permission.objects.get(codename="tbi.may_edit")
        view_permission = Permission.objects.get(codename="tbi.may_view")
        publish_permission = Permission.objects.get(codename="tbi.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbi.may_publish_self")
        # Create a user with all permission
        self.user = User.objects.create_user(username='test-staff',
                                             password='test-staff')
        self.user.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission,
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        # Create a user that cant self publish editor 1
        self.user_editor = User.objects.create_user(username='test-editor',
                                                    password='test-editor')
        self.user_editor.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
        )
        self.user_editor.is_staff = True
        self.user_editor.save()
        # Create a user that cant self publish editor 2
        self.user_editor_two = User.objects.create_user(username='editor',
                                                        password='editor')
        self.user_editor_two.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
        )
        self.user_editor_two.is_staff = True
        self.user_editor_two.save()
        # Create client for user
        self.user_editor_client = Client()
        self.user_editor_two_client = Client()
        # Log user into the client
        self.client.login(username='test-staff', password='test-staff')
        self.user_editor_client.login(
            username='test-editor', password='test-editor')
        self.user_editor_two_client.login(
            username='editor', password='editor')
        # Take the session id cookie for log into selenium
        self.cookie_admin = self.client.cookies['sessionid'].value
        self.cookie_editor = self.user_editor_client.cookies['sessionid'].value
        self.cookie_editor_two = (self.user_editor_two_client
                                  .cookies['sessionid'].value)
        """ Launch the browser the path of the browser will be
         auto added with the webdriver_manager package and wait 10 sec
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.selenium = WebDriver(ChromeDriverManager().install(),
                                  options=options)

        self.selenium.implicitly_wait(5)

    def tearDown(self):
        # Close the browser
        self.selenium.quit()

    def fill_the_form_and_publish(self, slug, title, body_1="body 1", body_2="body 2",
                                  body_3="body 3", edit=False):
        """Fill the topicblog item form and publish
        """
        if not edit:
            slug_input = self.selenium.find_element_by_name("slug")
            slug_input.send_keys(slug)
        title_input = self.selenium.find_element_by_name("title")
        title_input.clear()
        title_input.send_keys(title)
        select = Select(self.selenium.find_element_by_name("template"))
        select.select_by_value("topicblog/content.html")
        self.selenium.find_element_by_link_text("Contenu (1)").click()
        body_text_1_md_input = self.selenium.find_element_by_id(
            "id_body_text_1_md")
        body_text_1_md_input.clear()
        body_text_1_md_input.send_keys(body_1)
        body_text_2_md_input = self.selenium.find_element_by_id(
            "id_body_text_2_md")
        body_text_2_md_input.clear()
        body_text_2_md_input.send_keys(body_2)
        self.selenium.find_element_by_link_text("Contenu (2)").click()
        body_text_3_md_input = self.selenium.find_element_by_id(
            "id_body_text_3_md")
        body_text_3_md_input.clear()
        body_text_3_md_input.send_keys(body_3)
        self.selenium.find_element_by_name("sauvegarder").click()
        self.selenium.find_element_by_xpath(
            "//input[@value='Publier']").click()

    def test_user_permited_create_auto_publish(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_admin,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.fill_the_form_and_publish("test-slug-staff", "title item")
        item_staff = TopicBlogItem.objects.filter(
            slug="test-slug-staff")[0]
        self.assertIsNotNone(
            item_staff, msg="The item created by the super user"
                            " is not in the database")
        # Go to the user view
        self.selenium.find_element_by_link_text("Visualiser (usager)").click()
        """Get the body innerHTML and check if
        this is what we send in the form
        """
        body_app_content = self.selenium.find_element_by_id("app_content")
        body_html = body_app_content.get_attribute('innerHTML')
        self.assertHTMLEqual(
            body_html, "<p>body 1</p><p>body 2</p><p>body 3</p>",
            msg="The body innerHTML is not the same"
                " as what we send to the form")

    def test_editor_create_item_but_cant_publish(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_editor,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        slug = 'test-slug-editor'
        self.fill_the_form_and_publish(slug, 'title item')
        # Check if the item is on the databse and the publication should equal to none.
        item_editor = TopicBlogItem.objects.filter(
            slug="test-slug-editor")[0]
        self.assertIsNotNone(item_editor,
                             msg="The item created by the editor"
                                 " is not in the database")
        self.assertIsNone(item_editor.publication_date,
                          msg="The publication date is not none")
        # Check if the user get the 403 Forbidden
        body = self.selenium.find_element_by_tag_name("body")
        body_html = body.get_attribute('innerHTML')
        self.assertHTMLEqual(body_html, "<h1>403 Forbidden</h1><p></p>",
                             msg="User can't self publish")
        # Check the user view
        self.selenium.get('%s%s' %
                          (self.live_server_url,
                           reverse("topic_blog:view_item_by_slug",
                                   kwargs={
                                       "the_slug": slug
                                   })
                           ))
        """Get the body innerHTML and check if
        this is not found because this is not published
        """
        body_view = self.selenium.find_element_by_tag_name("body")
        body_view_html = body_view.get_attribute('innerHTML')
        self.assertHTMLEqual(body_view_html,
                             "<h1>Not Found</h1><p>The requested resource "
                             "was not found on this server.</p>")

    def test_editor_create_and_another_publish(self):
        # Create an item with the first editor that is not published
        self.item = TopicBlogItem.objects.create(
            slug="test-slug",
            user=self.user_editor,
            template_name="topicblog/content.html",
            body_text_1_md="body 1",
            body_text_2_md="body 2",
            body_text_3_md="body 3",
            title="Test-title")
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_editor_two,
             'secure': False, 'path': '/'})
        # Go to the admin view of the item that the first editor as created
        self.selenium.get('%s%s' %
                          (self.live_server_url,
                           reverse("topic_blog:view_item_by_pkid",
                                   kwargs={
                                       "pkid": self.item.id,
                                       "the_slug": self.item.slug,
                                   })
                           ))
        self.selenium.find_element_by_xpath(
            "//input[@value='Publier']").click()
        item_editor = TopicBlogItem.objects.filter(
            slug="test-slug")[0]
        # Check if publication date and first publication date is NOT none
        self.assertIsNotNone(item_editor.publication_date,
                             msg="The publication date should not be none")
        self.assertIsNotNone(item_editor.first_publication_date,
                             msg="The first publication date"
                                 "should not be none")
        # Check the user view
        self.selenium.find_element_by_link_text("Visualiser (usager)").click()
        """Get the body innerHTML and check if
        this is what we send in the form
        """
        body_app_content = self.selenium.find_element_by_id("app_content")
        body_html = body_app_content.get_attribute('innerHTML')
        self.assertHTMLEqual(
            body_html, "<p>body 1</p><p>body 2</p><p>body 3</p>",
            msg="The body innerHTML is not the same"
                " as what we send to the form")

    def test_edit_and_self_publish(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_admin,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.fill_the_form_and_publish(slug="test-edited", title="title-edit")
        # Go to the edit view
        self.selenium.find_element_by_link_text("Modifier").click()
        self.fill_the_form_and_publish(slug="", title="new title edited",
                                       body_1="new setence 1",
                                       body_2="new setence 2",
                                       body_3="new setence 3")

        # Check if the new title is on the database
        item_edited = TopicBlogItem.objects.filter(
            title="new title edited")[0]

        self.assertIsNotNone(item_edited,
                             msg="The item edited by the staff"
                             " is not in the database")
        # Go to the user view
        self.selenium.find_element_by_link_text("Visualiser (usager)").click()
        """Get the body innerHTML and check if
        this is what we send in the form
        """
        body_app_content = self.selenium.find_element_by_id("app_content")
        body_html = body_app_content.get_attribute('innerHTML')
        self.assertHTMLEqual(
            body_html, "<p>new setence 1</p><p>new setence 2</p><p>new setence 3</p>",
            msg="The body innerHTML is not the same"
                " as what we send to the form")

    def test_publish_an_unpublishable_item(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        self.selenium.add_cookie(
            {'name': 'sessionid', 'value': self.cookie_admin,
             'secure': False, 'path': '/'})
        self.selenium.get('%s%s' % (self.live_server_url,
                          reverse("topic_blog:new_item")))
        slug_input = self.selenium.find_element_by_name("slug")
        slug_input.send_keys("unpublishable")
        select = Select(self.selenium.find_element_by_name("template"))
        select.select_by_value("topicblog/content.html")
        self.selenium.find_element_by_name("sauvegarder").click()
        # Check if the item is on the databse and get the data for faking the publish
        item_unpublishable = TopicBlogItem.objects.filter(
            slug="unpublishable")[0]

        self.assertIsNotNone(item_unpublishable,
                             msg="The item created by the staff"
                                 " is not in the database")
        # testing with the unpublishable item of the staff
        response_0 = self.client.post(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": item_unpublishable.id,
                        "the_slug": item_unpublishable.slug
                    })
        )
        self.assertEqual(response_0.status_code, 500,
                         msg="try to pubilsh unpublishable item should return"
                             "HttpResponseServerError(code 500)")


class TopicBlogEmailFormTest(LiveServerTestCase, TestCase):
    """
    Test the form to send TBEmails through email.
    """

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        settings.DEBUG = True
        # Creation of users
        self.superuser = User.objects.create_superuser(
            username="test_user",
            email="admin@mobilitain.fr",
            password="test_password")
        self.no_permissions_user = User.objects.create_user(
            username="user_without_permissions",
            email="test@mobilitain.fr"
        )
        # Creation of content (article + mailinglist)
        self.email_article = TopicBlogEmail.objects.create(
            subject="Test subject",
            user=self.superuser,
            body_text_1_md="Test body text 1",
            slug="test-email",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            template_name="topicblog/content_email.html",
            title="Test title")
        self.mailing_list = MailingList.objects.create(
            mailing_list_name="the_mailing_list_name",
            mailing_list_token="the_mailing_list_token",
            contact_frequency_weeks=12,
            list_active=True)
        self.mailing_list.save()
        # Because we can be redirected to index, we create a TBItem to load the
        # page properly
        self.index_page = TopicBlogItem.objects.create(
            slug="index",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=9),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.superuser,
            body_text_1_md="body 1",
            body_text_2_md="body 2",
            body_text_3_md="body 3",
            template_name="topicblog/content.html",
            title="Test-title")

        # Subscription of users to the mailing list
        subscribe_user_to_list(self.superuser, self.mailing_list)
        subscribe_user_to_list(self.no_permissions_user, self.mailing_list)

        # Retrieval of session cookies to allow Selenium to
        # act as a logged user
        self.no_permissions_client = Client()
        self.admin_client = Client()
        self.admin_client.login(
            username=self.superuser.username,
            password="test_password")
        self.admin_cookie = self.admin_client.cookies['sessionid'].value
        self.no_permissions_client.login(
            username=self.no_permissions_user.username,
            password="test_password")
        # Make the client get a session id
        # Superuser's session id doesn't need that
        self.no_permissions_client.get("/")
        self.no_permissions_cookie = \
            self.no_permissions_client.cookies['sessionid'].value

        # Selenium setup
        options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--disable-extensions")
        self.driver = WebDriver(ChromeDriverManager().install(),
                                options=options)

        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.quit()
        super().tearDown()

    def act_as(self, sessionid: str) -> WebDriver:
        """
        Return a selenium driver that acts as a given user.
        """
        # Loads the dashboard, because it's a page that doesn't
        # have any permissions or requirements.
        self.driver.get('%s%s' % (self.live_server_url,
                                  reverse("dashboard:index")))
        self.driver.add_cookie(
            {'name': 'sessionid', 'value': sessionid,
             'secure': False, 'path': '/'})
        self.driver.get('%s%s' % (self.live_server_url,
                                  reverse("dashboard:index")))
        return self.driver

    def test_send_email_to_mailing_list(self):
        """
        Gets the sending form and send a mail to a given
        mailing list.
        """
        # Go to the sending form as admin
        self.driver = self.act_as(self.admin_cookie)
        url = self.live_server_url + reverse(
            "topic_blog:send_email", args=[self.email_article.slug])

        print("Before getting the form :", MailingList.objects.all())
        self.driver.get(url)
        WebDriverWait(self.driver, 2).until(
            lambda driver: driver.find_element_by_tag_name('body'))
        print("After getting the form :", MailingList.objects.all())
        # Select the mailing list in the form's dropdown
        dropdown = Select(self.driver.find_element(By.ID, "id_mailing_list"))
        dropdown.select_by_visible_text("the_mailing_list_name")

        # Confirm selection
        self.driver.find_element(By.NAME, "send-to-mailing-list").click()

        # Wait until the success page is loaded
        WebDriverWait(self.driver, 10).until(
            EC.title_is(self.index_page.title)
            )

        # 2 : one for the superuser and one for the no_perm_user
        number_of_recipients = \
            len(get_subcribed_users_email_list(self.mailing_list))

        self.assertEqual(number_of_recipients, 2)

        # test that a mail has been sent to the 2 subscribers
        self.assertEqual(len(mail.outbox), number_of_recipients)
