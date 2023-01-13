from datetime import datetime, timezone

from django.contrib.auth.models import Permission, User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .models import Event, InappropriateFlag, MobilitoSession, MobilitoUser
from .views import TutorialState


class TutorialStateTests(TestCase):
    def setUp(self):
        self.tutorial_state = TutorialState()

    def test_static_state(self):
        self.assertEqual(self.tutorial_state.default_page(), "presentation")
        self.assertEqual(
            self.tutorial_state.canonical_page("presentation"), "presentation"
        )
        self.assertEqual(self.tutorial_state.canonical_page("velos"), "velos")
        self.assertEqual(
            self.tutorial_state.canonical_page("unknown"), "presentation"
        )


class TutorialViewTests(TestCase):
    def setUp(self):
        self.tutorial_state = TutorialState()

    def test_state_progression(self):
        client = Client()
        response_1 = client.get(
            reverse(
                "mobilito:tutorial", kwargs={"tutorial_page": "presentation"}
            )
        )
        self.assertEqual(response_1.status_code, 200)
        next_page = response_1.context["next_page"]
        # A too-weak constraint.
        self.assertTrue(next_page in self.tutorial_state.all_tutorial_pages)


class MobilitoSessionViewTests(TestCase):
    def setUp(self):
        # Creation of a MobilitoSession object
        user = User.objects.create(username="foo", password="bar")
        self.user = MobilitoUser.objects.create(user=user)
        self.mobilito_session = MobilitoSession.objects.create(
            user=self.user,
            start_timestamp=datetime.now(timezone.utc),
            location="Foo",
        )
        self.mobilito_session_url = reverse_lazy(
            "mobilito:mobilito_session_summary",
            args=[self.mobilito_session.session_sha1],
        )
        self.flag_session_url = reverse_lazy(
            "mobilito:flag_session", args=[self.mobilito_session.session_sha1]
        )
        self.update_location_url = reverse_lazy(
            "mobilito:edit_location", args=[self.mobilito_session.session_sha1]
        )

        # User with permission to view unpublished  mobilito sessions
        self.authorised_user = User.objects.create(
            username="bar", password="foo"
        )
        may_view_sessions = Permission.objects.get(
            codename="mobilito_session.view_session"
        )
        may_edit_sessions = Permission.objects.get(
            codename="change_mobilitosession"
        )
        self.authorised_user.user_permissions.add(may_view_sessions)
        self.authorised_user.user_permissions.add(may_edit_sessions)

        # Creating 3 clients for each user type :
        # - author_client : Is the MobilitoSession's creator (author)
        # - authorised_client : Is a user with permission to view the session
        # - Anonymous client : Is a user without permission to view the session
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
            {
                "client": self.author_client,
                "code": 200,
                "msg": "MobilitoSession's author is able to see this page",
            },
            {
                "client": self.anonymous_client,
                "code": 404,
                "msg": ("Anon users can't have access to this page."),
            },
            {
                "client": self.authorised_user_client,
                "code": 200,
                "msg": "The page must return 200 the user has the permission.",
            },
        ]
        self.no_perm_needed_responses = [
            {
                "client": self.author_client,
                "code": 200,
                "msg": (
                    "The page must return 200, permission is not mandatory."
                ),
            },
            {
                "client": self.anonymous_client,
                "code": 200,
                "msg": (
                    "The page must return 200, permission is not mandatory."
                ),
            },
            {
                "client": self.authorised_user_client,
                "code": 200,
                "msg": (
                    "The page must return 200, permission is not mandatory."
                ),
            },
        ]

    def test_mobilito_session_view(self):
        """Test the ability to see a mobilito_session that is published and
        doesn't require permission.

        """
        for client_code in self.no_perm_needed_responses:
            response = client_code["client"].get(self.mobilito_session_url)
            self.assertEqual(
                response.status_code, client_code["code"], client_code["msg"]
            )

    def test_mobilito_session_view_unpublished(self):
        """Test the ability to see a mobilito_session that is not published."""
        self.mobilito_session.published = False
        self.mobilito_session.save()
        for client_code in self.perm_needed_responses:
            response = client_code["client"].get(self.mobilito_session_url)
            self.assertEqual(
                response.status_code, client_code["code"], client_code["msg"]
            )

    def test_flag_session(self):
        """Test the ability flag a session."""

        # GET method is not allowed
        for clients in self.no_perm_needed_responses:
            response = clients["client"].get(self.flag_session_url)
            self.assertEqual(
                response.status_code, 405, "GET method is not allowed."
            )

        # POST method is allowed for authenticated users
        post_data = {
            "report-abuse-text": "This is a test report.",
        }
        response = self.anonymous_client.post(self.flag_session_url, post_data)
        self.assertEqual(
            response.status_code,
            200,
            "POST method is allowed for anonymous users",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            1,
            "An InappropriateFlag must be created",
        )

        response = self.authorised_user_client.post(
            self.flag_session_url, post_data
        )
        self.assertEqual(
            response.status_code,
            200,
            "POST method is allowed for authorised users.",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            2,
            "An InappropriateFlag must be created.",
        )

        # Trying to flag a session twice doesn't create a new record.
        response = self.authorised_user_client.post(
            self.flag_session_url, post_data
        )
        self.assertEqual(
            response.status_code,
            200,
            "POST method is allowed for authorised users.",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            2,
            "User may flag only once for a given session",
        )

        response = self.anonymous_client.post(self.flag_session_url, post_data)
        self.assertEqual(
            response.status_code,
            200,
            "POST method is allowed for anonymous users",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            2,
            "Anonymous users may flag only once for "
            "a given mobilito session",
        )

        # Trying to flag a session that doesn't exist returns a 404
        response = self.authorised_user_client.post(
            reverse_lazy("mobilito:flag_session", args=["foo"]), post_data
        )
        self.assertEqual(
            response.status_code,
            404,
            "Users can't flag a session that doesn't exist.",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            2,
            (
                "No new report should be created when there isn't a"
                " matching MobilitoSession."
            ),
        )

        response = self.anonymous_client.post(
            reverse_lazy("mobilito:flag_session", args=["foo"]), post_data
        )
        self.assertEqual(
            response.status_code,
            404,
            "Anonymous users can't flag a Mobilito Session that doesn't "
            "exist.",
        )
        self.assertEqual(
            InappropriateFlag.objects.count(),
            2,
            (
                "No new report should be created when there isn't a"
                " matching mobilitoSession."
            ),
        )

    def test_presence_of_edit_button(self):
        """Test the presence of the edit button."""
        button_id = "mobilito-session-edit-btn"

        response = self.author_client.get(self.mobilito_session_url)
        self.assertContains(response, button_id)

        response = self.authorised_user_client.get(self.mobilito_session_url)
        self.assertContains(response, button_id)

        response = self.anonymous_client.get(self.mobilito_session_url)
        self.assertNotContains(response, button_id)

    def test_ability_to_edit_session_location(self):
        """Test the ability to edit a session location."""
        post_data = {
            "location": "New location",
        }
        response = self.author_client.post(self.update_location_url, post_data)
        self.assertRedirects(response, self.mobilito_session_url)
        self.mobilito_session.refresh_from_db()
        self.assertEqual(self.mobilito_session.location, "New location")

        post_data = {
            "location": "Bar",
        }
        response = self.authorised_user_client.post(
            self.update_location_url, post_data
        )
        self.assertRedirects(response, self.mobilito_session_url)
        self.mobilito_session.refresh_from_db()
        self.assertEqual(self.mobilito_session.location, "Bar")

        post_data = {
            "location": "Foo",
        }
        response = self.anonymous_client.post(
            self.update_location_url, post_data
        )
        self.assertRedirects(response, self.mobilito_session_url)
        self.mobilito_session.refresh_from_db()
        self.assertEqual(self.mobilito_session.location, "Bar")


class SessionHistoryViewTests(TestCase):
    """Test the my session history view."""

    def setUp(self):
        # Creation of a MobilitoSession object
        user = User.objects.create(username="foo", password="bar")
        self.user = MobilitoUser.objects.create(user=user)
        self.mobilito_session = MobilitoSession.objects.create(
            user=self.user,
            start_timestamp=datetime.now(timezone.utc),
            location="Foo",
        )
        self.second_mobilito_session = MobilitoSession.objects.create(
            user=self.user,
            start_timestamp=datetime.now(timezone.utc),
            location="Bar",
        )
        self.mobilito_session_url = reverse_lazy(
            "mobilito:mobilito_session_summary",
            args=[self.mobilito_session.session_sha1],
        )
        self.second_mobilito_session_url = reverse_lazy(
            "mobilito:mobilito_session_summary",
            args=[self.second_mobilito_session.session_sha1],
        )

    def test_session_history(self):
        """Test the session history page."""
        # Testing that anon users can access the page.
        response = self.client.get(
            reverse_lazy(
                "mobilito:user_sessions", args=[self.user.user.username]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mobilito_session_url)
        self.assertContains(response, self.second_mobilito_session_url)

        response = self.client.get(
            reverse("mobilito:user_sessions", args=["doesn't exist"])
        )
        # Redirect to login
        self.assertEqual(response.status_code, 302)

    def test_index_display_of_session_history(self):
        """Test that the last sessions are displayed on mobilito's index."""
        response = self.client.get(reverse_lazy("mobilito:index"))
        self.assertContains(response, self.mobilito_session_url)
        self.assertContains(response, self.second_mobilito_session_url)

        self.mobilito_session.delete()
        response = self.client.get(reverse_lazy("mobilito:index"))
        self.assertContains(response, self.second_mobilito_session_url)
        self.assertNotContains(response, self.mobilito_session_url)

        # Create a new session from another user and check that it is
        # displayed on the index page.
        self.user_2 = MobilitoUser.objects.create(
            user=User.objects.create(username="test-username")
        )
        self.mobilito_session_2 = MobilitoSession.objects.create(
            user=self.user_2,
            start_timestamp=datetime.now(timezone.utc),
            location="Foo",
        )
        response = self.client.get(reverse_lazy("mobilito:index"))
        self.assertContains(response, self.second_mobilito_session_url)
        self.assertContains(
            response, self.mobilito_session_2.get_absolute_url()
        )
        self.assertNotContains(response, self.mobilito_session_url)

        self.user.user.username = "My cool username"
        self.user.user.save()
        response = self.client.get(reverse_lazy("mobilito:index"))
        self.assertContains(response, self.user.user.username)
        self.assertContains(
            response, self.mobilito_session_2.get_absolute_url()
        )


class MobilitoFlagSessionSeleniumTests(StaticLiveServerTestCase):
    """Test the flag session page using Selenium."""

    def setUp(self):
        MobilitoSessionViewTests.setUp(self)
        Event.objects.create(
            mobilito_session=self.mobilito_session,
            timestamp=datetime.now(),
            event_type="ped",
        )
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    def test_flag_session(self):
        """Test the ability to flag a session."""
        self.browser.get(self.live_server_url + self.mobilito_session_url)
        # Click might fail because the fontAwesome icon is not ready
        # but hitting enter on the dropdown menu will work to open it
        self.browser.find_element(By.ID, "dropdownMenuLink").send_keys(
            Keys.ENTER
        )
        self.browser.find_element(By.ID, "report-abuse").click()
        self.browser.find_element(By.ID, "report-abuse-text").send_keys(
            "This is a test report."
        )
        self.submit_button = self.browser.find_element(
            By.CSS_SELECTOR, "#report-abuse-form button"
        )

        def click_until_button_is_ready(browser: webdriver.Chrome) -> bool:
            """Click the submit button until it is ready.

            The submit button is present but not ready to be used before
            a little bit of time. This function will click the button
            until it is ready.
            """
            callable = EC.invisibility_of_element_located(
                (By.ID, "report-abuse-form")
            )
            modal_disappeared = callable(browser)
            if not modal_disappeared:
                self.submit_button.click()

            return bool(modal_disappeared)

        WebDriverWait(self.browser, 10).until(click_until_button_is_ready)

        self.assertEqual(
            InappropriateFlag.objects.count(),
            1,
            "An InappropriateFlag must be created",
        )


class MobilitoEditUsernameSeleniumTests(StaticLiveServerTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test-username", password="test-password"
        )
        self.mobilito_user = MobilitoUser.objects.create(user=self.user)
        self.mobilito_session = MobilitoSession.objects.create(
            user=self.mobilito_user,
            start_timestamp=datetime.now(timezone.utc),
            location="Bar",
        )
        self.user_2 = User.objects.create_user(
            username="JohnDoe", password="test-password-2"
        )
        self.mobilito_user_2 = MobilitoUser.objects.create(user=self.user_2)
        self.mobilito_session_2 = MobilitoSession.objects.create(
            user=self.mobilito_user_2,
            start_timestamp=datetime.now(timezone.utc),
            location="Foo",
        )
        user_1_client = Client()
        user_1_client.login(username="test-username", password="test-password")
        self.user_1_login_cookie = user_1_client.cookies["sessionid"].value
        user_2_client = Client()
        user_2_client.login(username="JohnDoe", password="test-password-2")
        self.user_2_login_cookie = user_2_client.cookies["sessionid"].value

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.browser.implicitly_wait(5)

    def login_as(self, login_cookie: str):
        """Log in as the user with the given login cookie."""
        self.browser.get(self.live_server_url + "/")
        self.browser.add_cookie(
            {
                "name": "sessionid",
                "value": login_cookie,
                "secure": False,
                "path": "/",
            }
        )

    def test_edit_username_in_place(self):
        """Test the ability to edit the username in place.

        Users should be able to click the edit icon and change their
        without changing pages.
        """
        self.login_as(self.user_1_login_cookie)
        self.browser.get(self.live_server_url + reverse("mobilito:index"))
        self.browser.find_element(
            By.ID,
            "mobilito-username-edit-btn_" + self.mobilito_session.session_sha1,
        ).click()
        input_field = self.browser.find_element(
            By.ID,
            "mobilito-username-input_" + self.mobilito_session.session_sha1,
        )
        input_field.clear()
        input_field.send_keys("MyCoolUsername")

        submit_button = self.browser.find_element(
            By.ID,
            "edit-username-submit-btn_" + self.mobilito_session.session_sha1,
        )
        submit_button.click()
        WebDriverWait(self.browser, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.ID,
                    "displayed-username_" + self.mobilito_session.session_sha1,
                ),
                "MyCoolUsername",
            )
        )
        self.assertEqual(
            self.browser.find_element(
                By.ID,
                "displayed-username_" + self.mobilito_session.session_sha1,
            ).text,
            "MyCoolUsername",
        )

    def test_edit_username_taken(self):
        """Test that the username cannot be changed to a taken username."""
        self.login_as(self.user_1_login_cookie)
        self.browser.get(self.live_server_url + reverse("mobilito:index"))
        self.browser.find_element(
            By.ID,
            "mobilito-username-edit-btn_" + self.mobilito_session.session_sha1,
        ).click()
        input_field = self.browser.find_element(
            By.ID,
            "mobilito-username-input_" + self.mobilito_session.session_sha1,
        )
        input_field.clear()
        input_field.send_keys("JohnDoe")

        submit_button = self.browser.find_element(
            By.ID,
            "edit-username-submit-btn_" + self.mobilito_session.session_sha1,
        )
        submit_button.click()
        WebDriverWait(self.browser, 5).until(
            EC.text_to_be_present_in_element(
                (
                    By.ID,
                    "displayed-username_" + self.mobilito_session.session_sha1,
                ),
                "test-username",
            )
        )
        self.assertEqual(
            self.browser.find_element(
                By.ID,
                "displayed-username_" + self.mobilito_session.session_sha1,
            ).text,
            "test-username",
        )
