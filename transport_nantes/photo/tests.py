from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from asso_tn.utils import make_timed_token
from mailing_list.models import MailingList, MailingListEvent

from .models import PhotoEntry, Vote


class TestUploadEntry(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        self.mailing_list = MailingList.objects.create(
            mailing_list_name='Operation pieton',
            mailing_list_token="operation-pieton")

    def test_get(self):
        response = self.client.get(reverse('photo:upload'))
        # Redirect to login page for anonymous users
        self.assertEqual(response.status_code, 302)

        response = self.auth_client.get(reverse('photo:upload'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        THIS_DIR = Path(__file__).resolve().parent
        FILE_PATH = THIS_DIR / 'test_data' / '1920x1080.png'
        with open(FILE_PATH, 'rb') as f:
            image = f.read()
        form_data = {
            'terms_and_condition_checkbox': True,
            'category': 'LE_TRAVAIL',
            'submitted_photo': SimpleUploadedFile(
                name='1920x1080.png',
                content=image,
                content_type='image/png',
            )
        }
        response = self.auth_client.post(
            reverse('photo:upload'),
            form_data,
        )
        # Redirect to confirmation page
        self.assertEqual(response.status_code, 302)

        # Check that the photo was saved
        photo_entry = PhotoEntry.objects.get(user=self.user)
        self.assertEqual(photo_entry.category, 'LE_TRAVAIL')
        entries_count = PhotoEntry.objects.count()
        self.assertEqual(entries_count, 1)


class TestConfirmation(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        THIS_DIR = Path(__file__).resolve().parent
        FILE_PATH = THIS_DIR / 'test_data' / '1920x1080.png'
        self.photo_entry = PhotoEntry.objects.create(
            user=self.user,
            category='LE_TRAVAIL',
        )
        with open(FILE_PATH, 'rb') as f:
            self.photo_entry.submitted_photo = ImageFile(
                f, name='1920x1080.png')
            self.photo_entry.save()
        self.encoded_object_id = make_timed_token(
            string_key="", int_key=self.photo_entry.id, minutes=60*24*30)

    def test_get(self):
        get_arg = "?submission=" + self.encoded_object_id
        response = self.client.get(reverse('photo:confirmation') + get_arg)
        self.assertEqual(response.status_code, 200)


class TestPhotoView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)
        THIS_DIR = Path(__file__).resolve().parent
        FILE_PATH = THIS_DIR / 'test_data' / '1920x1080.png'
        self.photo_entry = PhotoEntry.objects.create(
            user=self.user,
            category='LE_TRAVAIL',
        )
        with open(FILE_PATH, 'rb') as f:
            self.photo_entry.submitted_photo = ImageFile(
                f, name='1920x1080.png')
            self.photo_entry.save()

        self.mailing_list = MailingList.objects.create(
            mailing_list_name='Operation pieton',
            mailing_list_token="operation-pieton")

    def test_get(self):

        # Anonymous client trying to see an unaccepted photo
        response = self.client.get(
            reverse('photo:photo_details', args=[self.photo_entry.sha1_name]))
        self.assertEqual(response.status_code, 403)

        # Photo entry's owner trying to see their photo
        response = self.auth_client.get(
            reverse('photo:photo_details', args=[self.photo_entry.sha1_name]))
        self.assertEqual(response.status_code, 200)

        # Anonymous client trying to see an unexisting photo
        response = self.client.get(
            reverse('photo:photo_details', args=['unexisting_sha1']))
        self.assertEqual(response.status_code, 404)

        # We now make the photo accepted
        self.photo_entry.accepted = True
        self.photo_entry.save()

        # Anonymous client trying to see an accepted photo
        response = self.client.get(
            reverse('photo:photo_details', args=[self.photo_entry.sha1_name]))
        self.assertEqual(response.status_code, 200)

        # Photo entry's owner trying to see their photo
        response = self.auth_client.get(
            reverse('photo:photo_details', args=[self.photo_entry.sha1_name]))
        self.assertEqual(response.status_code, 200)

    def test_post_form_valid(self):
        url = reverse('photo:photo_details', args=[self.photo_entry.sha1_name])
        # Users trying to vote on an unaccepted photo
        post_data = {
            "vote_value": "upvote",
            "photoentry_sha1_name": self.photo_entry.sha1_name,
            "captcha_0": "dummy-value",
            "captcha_1": "PASSED",
            "email_address": "test@example.com",
        }
        response = self.client.post(url, post_data,)
        self.assertEqual(response.status_code, 403)
        response = self.auth_client.post(url, post_data,)
        self.assertEqual(response.status_code, 403)

        # We accept the photo
        self.photo_entry.accepted = True
        self.photo_entry.save()

        # Users trying to vote on an accepted photo for the first time
        response = self.client.post(url, post_data,)
        self.assertEqual(response.status_code, 200)
        response = self.auth_client.post(url, post_data,)
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
        response = self.client.post(url, post_data,)
        self.assertEqual(response.status_code, 200)
        response = self.auth_client.post(url, post_data,)
        self.assertEqual(response.status_code, 200)

        # Checking that the votes were saved
        votes_count = Vote.objects.count()
        self.assertEqual(votes_count, 2)

        # Checking that we did not subscribe the users to the newsletter
        self.assertEqual(MailingListEvent.objects.count(), 0)

    def test_post_form_invalid(self):
        url = reverse('photo:photo_details', args=[self.photo_entry.sha1_name])
        self.photo_entry.accepted = True
        self.photo_entry.save()
        # Users fail the captcha
        post_data = {
            "vote_value": "downvote",
            "photoentry_sha1_name": self.photo_entry.sha1_name,
            "captcha_0": "dummy-value",
            "captcha_1": "ERROR",
        }
        response = self.client.post(url, post_data,)
        self.assertEqual(response.status_code, 200)
        # Auth clients do not have captcha to fill
        response = self.auth_client.post(url, post_data,)
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
