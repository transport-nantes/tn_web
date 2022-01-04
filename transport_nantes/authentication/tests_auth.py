from django.contrib.auth.models import User
from django.test import TestCase
import datetime

from django.urls.base import reverse

from asso_tn.utils import make_timed_token, token_valid


class TimedTokenTest(TestCase):

    def test_expiry(self):
        """Test token expiration.

        Test that the token remains valid for the time we expect and
        not after.

        """
        EMAIL = "joe@example.com"
        EXPIRY_MINUTES = 2
        EXPIRY_SECONDS = EXPIRY_MINUTES * 60
        NOW = datetime.datetime.now().timestamp()
        for persisted in [0, 1]:
            token = make_timed_token(EMAIL, EXPIRY_MINUTES, persisted, NOW)
            now_response = token_valid(token, NOW)
            self.assertEqual(now_response[0], EMAIL)
            self.assertEqual(now_response[1], persisted)
            before_response = token_valid(token, NOW + EXPIRY_SECONDS - 1)
            self.assertEqual(before_response[0], EMAIL)
            self.assertEqual(before_response[1], persisted)
            after_response = token_valid(token, NOW + EXPIRY_SECONDS + 1)
            self.assertEqual(after_response[0], None)
            self.assertEqual(after_response[1], 0)


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='joe',
            password='password',
            email="joe@potus.com"
        )
        self.pass_user = User.objects.create_user(
            username='pass-joe',
            password='password',
            email="passjoe@potus.com"
        )
        self.pass_user.profile.authenticates_by_mail = False
        self.pass_user.save()

    def test_form_valid(self):
        """Tests status code of LoginView when form is valid.
        """
        remember_me = 0

        # POST existing user
        response = self.client.post(
            reverse("authentication:login"),
            {
                "email": self.user.email,
                "remember_me": remember_me,
                "captcha_0": "dummy-value",
                "captcha_1": "PASSED",
            }
        )
        self.assertEqual(response.status_code, 200)

        # POST non-existing user
        response = self.client.post(
            reverse("authentication:login"),
            {
                "email": "doesntexist@null.com",
                "remember_me": remember_me,
                "captcha_0": "dummy-value",
                "captcha_1": "PASSED",
            }
        )
        # Expected to 200, displays an "Email sent" page.
        self.assertEqual(response.status_code, 200)

        # POST existing user with password login
        response = self.client.post(
            reverse("authentication:login"),
            {
                "email": self.pass_user.email,
                "remember_me": remember_me,
                "captcha_0": "dummy-value",
                "captcha_1": "PASSED",
            }
        )
        # print("Response :", response)
        # Expected to redirect to password login page.
        # Printing the response shows it is a redirect to
        # /auth/pass/<token>, but I have no idea how to test that
        # since I don't have a way to know the token before it is generated.
        self.assertEqual(response.status_code, 302)


class PasswordLoginViewTest(TestCase):

    def setUp(self):
        # Create a token for password login.
        EMAIL = "passjoe@potus.com"
        EXPIRY_MINUTES = 2
        NOW = datetime.datetime.now().timestamp()
        self.token = make_timed_token(EMAIL, EXPIRY_MINUTES, 0, NOW)

        self.pass_user = User.objects.create_user(
            username='pass-joe',
            password='password',
            email="passjoe@potus.com"
        )
        self.pass_user.profile.authenticates_by_mail = False
        self.pass_user.save()

    def test_password_login_status_code(self):
        """Tests status code of PasswordLoginView when form is valid.
        """
        response = self.client.post(
            reverse("authentication:password_login",
                    kwargs={"token": self.token}),
            {
                "email": self.pass_user.email,
                "password": "password",
                "remember_me": 1,
            }
        )
        # Redirect to main page if valid login
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        response = self.client.post(
            reverse("authentication:password_login",
                    kwargs={"token": self.token}),
            {
                "email": self.pass_user.email,
                "password": "wrongpassword",
                "remember_me": 0,
            }
        )
        # Redirect to the same page with a different token if invalid login
        self.assertEqual(response.status_code, 302)

    def test_password_login_get(self):
        """Tests status code of PasswordLoginView when form is valid.
        """
        # Get with a valid token
        response = self.client.get(
            reverse("authentication:password_login",
                    kwargs={"token": self.token})
        )
        self.assertEqual(response.status_code, 200)

        # Get with an invalid token
        response = self.client.get(
            reverse("authentication:password_login",
                    kwargs={"token": "invalid-token"})
        )
        # Redirection to mail login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("authentication:login"))


class ActivationLoginViewTest(TestCase):

    def setUp(self):
        # Create a token for password login.
        EMAIL = "passjoe@potus.com"
        EXPIRY_MINUTES = 2
        NOW = datetime.datetime.now().timestamp()
        self.token = make_timed_token(EMAIL, EXPIRY_MINUTES, 0, NOW)

        self.pass_user = User.objects.create_user(
            username='pass-joe',
            password='password',
            email=EMAIL,)
        self.pass_user.profile.authenticates_by_mail = False
        self.pass_user.is_active = False
        self.pass_user.save()

    def test_activate_valid_token(self):
        """Tests the activate function when given a valid token"""
        response = self.client.get(
            reverse("authentication:activate", kwargs={"token": self.token})
        )
        self.assertEqual(response.status_code, 200)

        user_is_active = response.context["user"].is_active
        self.assertEqual(user_is_active, True)

        user_confirmed_mail = response.context["user"].profile.email_confirmed
        self.assertEqual(user_confirmed_mail, True)

        user_is_logged_in = response.context["user"].is_authenticated
        self.assertEqual(user_is_logged_in, True)

    def test_activate_invalid_token(self):
        """Tests the activate function when given an invalid token"""
        response = self.client.get(
            reverse("authentication:activate",
                    kwargs={"token": "invalid-token"})
        )
        self.assertEqual(response.status_code, 200)

        user_is_active = response.context["user"].is_active
        self.assertEqual(user_is_active, False)

        user_is_anonymous_user = response.context["user"].is_anonymous
        self.assertEqual(user_is_anonymous_user, True)

        user_is_logged_in = response.context["user"].is_authenticated
        self.assertEqual(user_is_logged_in, False)


class DeauthViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='joe',
            password='password',
            email="joe@potus.com"
        )
        self.client.login(username='joe', password='password')

    def test_deauth_status_code(self):
        """Tests the deauth view status code"""
        response = self.client.get(reverse("authentication:logout"))
        # Redirection to index
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        # Since redirection response don't hold user, we get another
        # response to check if user is logged out.
        response = self.client.get(reverse("authentication:login"))
        user_is_logged_in = response.context["user"].is_authenticated
        self.assertEqual(user_is_logged_in, False)
