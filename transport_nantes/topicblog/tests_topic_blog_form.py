from datetime import datetime, timezone
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import Permission, User
from django.test import LiveServerTestCase, Client
from selenium.webdriver.support.ui import Select, WebDriverWait
from django.urls import reverse
from django.core import mail
from asso_tn.utils import make_timed_token

from mailing_list.events import get_subcribed_users_email_list, subscribe_user_to_list
from mailing_list.models import MailingList, MailingListEvent
from .models import TopicBlogEmail, TopicBlogEmailSendRecord, TopicBlogItem
from selenium.webdriver.chrome.options import Options


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

