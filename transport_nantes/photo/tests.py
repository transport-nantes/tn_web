from pathlib import Path

import bs4 as bs
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from asso_tn.utils import make_timed_token
from mailing_list.models import MailingList, MailingListEvent

from .models import PhotoEntry, Vote


def add_image_for_test(test_self, accepted=False, sha1_name=None):
    """Add a (fixed) image for a unit test."""
    k_this_dir = Path(__file__).resolve().parent
    k_file_path = k_this_dir / "test_data" / "1920x1080.png"
    test_self.photo_entry = PhotoEntry.objects.create(
        user=test_self.user,
        category="LE_TRAVAIL",
        accepted=accepted,
        sha1_name=sha1_name,
    )
    with open(k_file_path, "rb") as fp_img:
        test_self.photo_entry.submitted_photo = ImageFile(
            fp_img, name="1920x1080.png"
        )
        test_self.photo_entry.save()


class TestUploadEntry(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.mailing_list = MailingList.objects.create(
            mailing_list_name="Operation pieton",
            mailing_list_token="operation-pieton",
        )

    def test_get(self):
        response = self.client.get(reverse("photo:upload"))
        # Redirect to login page for anonymous users
        self.assertEqual(response.status_code, 302)

        response = self.auth_client.get(reverse("photo:upload"))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        k_this_dir = Path(__file__).resolve().parent
        k_file_path = k_this_dir / "test_data" / "1920x1080.png"
        with open(k_file_path, "rb") as f:
            image = f.read()
        form_data = {
            "terms_and_condition_checkbox": True,
            "category": "LE_TRAVAIL",
            "submitted_photo": SimpleUploadedFile(
                name="1920x1080.png",
                content=image,
                content_type="image/png",
            ),
        }
        response = self.auth_client.post(
            reverse("photo:upload"),
            form_data,
        )
        # Redirect to confirmation page
        self.assertEqual(response.status_code, 302)

        # Check that the photo was saved
        photo_entry = PhotoEntry.objects.get(user=self.user)
        self.assertEqual(photo_entry.category, "LE_TRAVAIL")
        entries_count = PhotoEntry.objects.count()
        self.assertEqual(entries_count, 1)


class TestConfirmation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        add_image_for_test(self)

        self.encoded_object_id = make_timed_token(
            string_key="", int_key=self.photo_entry.id, minutes=60 * 24 * 30
        )

    def test_get(self):
        get_arg = "?submission=" + self.encoded_object_id
        response = self.client.get(reverse("photo:confirmation") + get_arg)
        self.assertEqual(response.status_code, 200)


class TestPhotoView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        add_image_for_test(self)

        self.mailing_list = MailingList.objects.create(
            mailing_list_name="Operation pieton",
            mailing_list_token="operation-pieton",
        )

    def test_get(self):
        # Anonymous client trying to see an unaccepted photo
        response = self.client.get(
            reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.assertEqual(response.status_code, 403)

        # Photo entry's owner trying to see their photo
        response = self.auth_client.get(
            reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.assertEqual(response.status_code, 200)

        # Anonymous client trying to see an unexisting photo
        response = self.client.get(
            reverse("photo:photo_details", args=["unexisting_sha1"])
        )
        self.assertEqual(response.status_code, 404)

        # We now make the photo accepted
        self.photo_entry.accepted = True
        k_photographer_id = "identify the photographer here"
        self.photo_entry.photographer_identifier = k_photographer_id
        k_ped_issues = "some pedestrian issues"
        self.photo_entry.pedestrian_issues_md = k_ped_issues
        k_submitter_info = "some interesting submitter info"
        self.photo_entry.submitter_info_md = k_submitter_info
        self.photo_entry.save()

        # Anonymous client trying to see an accepted photo
        response = self.client.get(
            reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.assertEqual(response.status_code, 200)
        soup = bs.BeautifulSoup(response.content, "html.parser")
        self.assertEqual(
            k_photographer_id, soup.find(id="photographer_ident").i.string
        )
        self.assertEqual(
            k_submitter_info, soup.find(id="submitter_info").p.string
        )
        self.assertEqual(k_ped_issues, soup.find(id="ped_issues").p.string)

        # Photo entry's owner trying to see their photo
        response = self.auth_client.get(
            reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.assertEqual(response.status_code, 200)

        # Anonymous client trying to see the photo gallery
        response = self.client.get(reverse("photo:galerie"))
        self.assertEqual(response.status_code, 200)

    def test_post_form_valid(self):
        url = reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        # Users trying to vote on an unaccepted photo
        post_data = {
            "vote_value": "upvote",
            "photoentry_sha1_name": self.photo_entry.sha1_name,
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
            "email_address": "test@example.com",
        }
        response = self.client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 403)
        response = self.auth_client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 403)

        # We accept the photo
        self.photo_entry.accepted = True
        self.photo_entry.save()

        # Users trying to vote on an accepted photo for the first time
        response = self.client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)
        response = self.auth_client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)

        # Checking that the votes were saved
        votes_count = Vote.objects.count()
        self.assertEqual(votes_count, 2)

        # Checking that we subscribed the users to the newsletter
        self.assertEqual(MailingListEvent.objects.count(), 2)

        # We reset MailingListEvent & votes
        MailingListEvent.objects.all().delete()
        Vote.objects.all().delete()

        # Users refused to consent to subscribe to the newsletter
        post_data["consent_box"] = True
        response = self.client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)
        response = self.auth_client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)

        # Checking that the votes were saved
        votes_count = Vote.objects.count()
        self.assertEqual(votes_count, 2)

        # Checking that we did not subscribe the users to the newsletter
        self.assertEqual(MailingListEvent.objects.count(), 0)

    def test_post_form_invalid(self):
        url = reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        self.photo_entry.accepted = True
        self.photo_entry.save()
        # Users fail the captcha
        post_data = {
            "vote_value": "downvote",
            "photoentry_sha1_name": self.photo_entry.sha1_name,
            "captcha_0": "dummy-value",
            "captcha_1": "ERROR",
        }
        response = self.client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)
        # Auth clients do not have captcha to fill
        response = self.auth_client.post(
            url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)

        # Checking that the votes were saved and marked as captcha failed
        votes_count = Vote.objects.count()
        self.assertEqual(votes_count, 2)
        # Anon user
        self.assertEqual(
            Vote.objects.filter(captcha_succeeded=False).count(), 1
        )
        # Auth user
        self.assertEqual(
            Vote.objects.filter(captcha_succeeded=True).count(), 1
        )


class TestPhotoGallery(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_display_zero(self):
        """Confirm that we are ok if no image is accepted.

        In particular, we should display an appropriate error.

        """
        response_1 = self.client.get(reverse("photo:galerie"))
        self.assertEqual(response_1.status_code, 200)

        # The previous and next images should 404 if we have no images.
        k_non_existant_image_name = "xxx"
        response_prev_1 = self.client.get(
            reverse(
                "photo:prev_photo_details",
                kwargs={"photo_sha1": k_non_existant_image_name},
            )
        )
        self.assertEqual(response_prev_1.status_code, 404)
        response_next_1 = self.client.get(
            reverse(
                "photo:next_photo_details",
                kwargs={"photo_sha1": k_non_existant_image_name},
            )
        )
        self.assertEqual(response_next_1.status_code, 404)

        # Add a non-accepted image: it should behave the same as no
        # image here.
        add_image_for_test(self, accepted=False, sha1_name="a")
        response_2 = self.client.get(reverse("photo:galerie"))
        self.assertEqual(response_2.status_code, 200)
        response_a = self.client.get(
            reverse("photo:photo_details", kwargs={"photo_sha1": "a"})
        )
        self.assertEqual(response_a.status_code, 403)

        response_a_prev = self.client.get(
            reverse("photo:prev_photo_details", kwargs={"photo_sha1": "a"})
        )
        self.assertEqual(response_a_prev.status_code, 404)
        response_a_next = self.client.get(
            reverse("photo:next_photo_details", kwargs={"photo_sha1": "a"})
        )
        self.assertEqual(response_a_next.status_code, 404)

    def test_display_one(self):
        """Confirm that we can display a sole image.

        Check that all goes well if we have precisely one image.

        """
        add_image_for_test(self, accepted=True, sha1_name="a")
        check_image_and_prev_next(self, "a", "a", "a")

        # Adding a non-accepted image should chane nothing.
        add_image_for_test(self, accepted=False, sha1_name="b")
        # Previous/Next links should point to the same image if there's only one.
        check_image_and_prev_next(self, "a", "a", "a")

    def test_display_several(self):
        """Confirm that we can display multiple images."""
        add_image_for_test(self, accepted=True, sha1_name="a")
        add_image_for_test(self, accepted=True, sha1_name="b")
        add_image_for_test(self, accepted=True, sha1_name="c")
        add_image_for_test(self, accepted=False, sha1_name="x")
        add_image_for_test(self, accepted=False, sha1_name="y")
        check_image_and_prev_next(self, "a", "c", "b")
        check_image_and_prev_next(self, "b", "a", "c")
        check_image_and_prev_next(self, "c", "b", "a")


def check_image_and_prev_next(
    test_self, this_sha1, prev_sha1, next_sha1
) -> None:
    response = test_self.client.get(
        reverse("photo:photo_details", kwargs={"photo_sha1": this_sha1})
    )
    test_self.assertEqual(response.status_code, 200)
    soup = bs.BeautifulSoup(response.content, "html.parser")
    prev_link = soup.find(id="photo_prev")
    test_self.assertIsNotNone(prev_link)
    prev_url = reverse(
        "photo:prev_photo_details", kwargs={"photo_sha1": this_sha1}
    )
    test_self.assertEqual(prev_url, prev_link.get("href"))
    next_link = soup.find(id="photo_next")
    test_self.assertIsNotNone(next_link)
    next_url = reverse(
        "photo:next_photo_details", kwargs={"photo_sha1": this_sha1}
    )
    test_self.assertEqual(next_url, next_link.get("href"))
    prev_response = test_self.client.get(prev_url)
    test_self.assertEqual(prev_response.status_code, 302)
    test_self.assertEqual(
        prev_response.url,
        reverse("photo:photo_details", kwargs={"photo_sha1": prev_sha1}),
    )
    next_response = test_self.client.get(next_url)
    test_self.assertEqual(next_response.status_code, 302)
    test_self.assertEqual(
        next_response.url,
        reverse("photo:photo_details", kwargs={"photo_sha1": next_sha1}),
    )


class TestVotes(StaticLiveServerTestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
        )

        k_this_dir = Path(__file__).resolve().parent
        k_file_path = k_this_dir / "test_data" / "1920x1080.png"
        self.photo_entry = PhotoEntry.objects.create(
            user=self.user,
            category="LE_TRAVAIL",
            accepted=True,
        )
        self.photo_entry_2 = PhotoEntry.objects.create(
            user=self.user,
            category="L_AMOUR",
            accepted=True,
        )
        self.photo_entry_3 = PhotoEntry.objects.create(
            user=self.user,
            category="PIETON_URBAIN",
        )
        self.photo_entry_4 = PhotoEntry.objects.create(
            user=self.user,
            category="LE_TRAVAIL",
            accepted=True,
        )
        with open(k_file_path, "rb") as f:
            self.photo_entry.submitted_photo = ImageFile(
                f, name="1920x1080.png"
            )
            self.photo_entry.save()

        self.mailing_list = MailingList.objects.create(
            mailing_list_name="Operation pieton",
            mailing_list_token="operation-pieton",
        )

        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.auth_user_cookie = self.auth_client.cookies["sessionid"].value

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.anon_browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.auth_browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        # Use the commented out code below if you want to login with selenium
        # self.auth_browser.get(self.live_server_url + reverse('/'))
        # self.auth_browser.add_cookie(
        #     {'name': 'sessionid', 'value': self.auth_user_cookie,
        #      'secure': False, 'path': '/'})

        self.anon_browser.implicitly_wait(5)
        self.auth_browser.implicitly_wait(5)

    # This class is an adaptation from Selenium's documentation:
    # https://selenium-python.readthedocs.io/waits.html#explicit-waits
    # This has been implemented in place of a polling on the database
    # because the polling was raising occasionally a table locked error
    # on the CI server. (#1077)
    # Instead we wait from the DOM to update as a response to the server.
    class ElementHasCssClass:
        """
        An expectation for checking that an element has a particular css class.

        locator - used to find the element
        does_not_have_class - used to check if the element does not have the css class
        returns the WebElement once it has the particular css class
        """

        def __init__(
            self, locator, css_class: str, does_not_have_class: bool = False
        ):
            self.locator = locator
            self.css_class = css_class
            self.rev = does_not_have_class

        def __call__(self, driver: webdriver.Chrome):
            # Finding the referenced element
            element = driver.find_element(*self.locator)
            if self.css_class in element.get_attribute("class"):
                return element and not self.rev
            else:
                return self.rev

    def test_vote_anon(self):
        # Anon user
        self.anon_browser.get(
            self.live_server_url
            + reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.anon_browser.find_element(By.ID, "upvote-button").click()
        self.anon_browser.find_element(By.ID, "id_captcha_1").send_keys(
            "PASSED"
        )
        self.submit_button = self.anon_browser.find_element(
            By.CSS_SELECTOR, "#first-vote-form button"
        )

        def click_until_button_is_ready(browser: webdriver.Chrome) -> bool:
            """Click the submit button until it is ready.

            The submit button is present but not ready to be used before
            a little bit of time. This function will click the button
            until it is ready.
            """
            the_callable = EC.invisibility_of_element_located(
                (By.ID, "first-vote-div")
            )
            # Returns True if the element is invisible in the provided browser
            modal_disappeared = the_callable(browser)
            if not modal_disappeared:
                self.submit_button.click()

            return bool(modal_disappeared)

        WebDriverWait(self.anon_browser, 5).until(click_until_button_is_ready)

        # We check the first vote was saved
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().captcha_succeeded, True)
        self.assertEqual(Vote.objects.first().user, None)
        self.assertEqual(Vote.objects.first().vote_value, True)

        # We now simply click on vote button again, this should produce a new Vote
        self.anon_browser.find_element(By.ID, "upvote-button").click()

        # The POST request can take some time to process, we wait until it's
        # done
        WebDriverWait(self.anon_browser, 10).until(
            # css class 'bg-blue-light' is present when the user has liked
            # the photo, and is removed when user clicks again
            self.ElementHasCssClass(
                (By.ID, "upvote-button"),
                "bg-blue-light",
                # We want the class to be absent
                does_not_have_class=True,
            )
        )

        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(Vote.objects.last().user, None)
        self.assertEqual(Vote.objects.last().vote_value, False)

    def test_vote_auth(self):
        # Login with selenium
        self.auth_browser.get(self.live_server_url)
        self.auth_browser.add_cookie(
            {
                "name": "sessionid",
                "value": self.auth_user_cookie,
                "secure": False,
                "path": "/",
            }
        )
        # Auth user
        self.auth_browser.get(
            self.live_server_url
            + reverse("photo:photo_details", args=[self.photo_entry.sha1_name])
        )
        self.auth_browser.find_element(By.ID, "upvote-button").click()

        WebDriverWait(self.auth_browser, 5).until(
            EC.visibility_of_element_located((By.ID, "first-vote-form"))
        )

        self.submit_button = self.auth_browser.find_element(
            By.CSS_SELECTOR, "#first-vote-form button"
        )

        def click_until_button_is_ready(browser: webdriver.Chrome) -> bool:
            """Click the submit button until it is ready.

            The submit button is present but not ready to be used before
            a little bit of time. This function will click the button
            until it is ready.
            """
            the_callable = EC.invisibility_of_element_located(
                (By.ID, "first-vote-div")
            )
            # Returns True if the element is invisible in the provided browser
            modal_disappeared = the_callable(browser)
            if not modal_disappeared:
                self.submit_button.click()

            return bool(modal_disappeared)

        WebDriverWait(self.auth_browser, 5).until(click_until_button_is_ready)

        # The POST request can take some time to process, we wait until it's
        # done
        WebDriverWait(self.auth_browser, 20).until(
            # css class 'bg-blue-light' is present when the user has liked
            # the photo, and is removed when user clicks again
            self.ElementHasCssClass(
                (By.ID, "upvote-button"),
                "bg-blue-light",
            )
        )

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().captcha_succeeded, True)
        self.assertEqual(Vote.objects.first().user, self.user)
        self.assertEqual(Vote.objects.first().vote_value, True)

        # We now simply click on vote button again, this should
        # produce a new Vote
        self.auth_browser.find_element(By.ID, "upvote-button").click()

        # The POST request can take some time to process, we wait until it's
        # done
        WebDriverWait(self.auth_browser, 5).until(
            # css class 'bg-blue-light' is present when the user has liked
            # the photo, and is removed when user clicks again
            self.ElementHasCssClass(
                (By.ID, "upvote-button"),
                "bg-blue-light",
                # We want the class to be absent
                does_not_have_class=True,
            )
        )

        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(Vote.objects.last().user, self.user)
        self.assertEqual(Vote.objects.last().vote_value, False)
