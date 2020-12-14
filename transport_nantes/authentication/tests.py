from django.test import TestCase, RequestFactory

from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import authentication.views as views
from asso_tn.utils import make_timed_token
from django.utils.crypto import get_random_string
from time import sleep
from captcha.models import CaptchaStore
# Create your tests here.

# TODO Test good printing of pages (first print, post, redirect) and also page needing token from mail
# TODO Test adding of new user if account doesn't exist and if account already exists
class UserTest(TestCase):

    # Add new user and test site page shown
    def test_add_new_user(self):

        # Set site into Site table
        site = Site.objects.get(id=1)
        site.domain = "localhost:8000"
        site.name = "localhost"
        site.save()

        # Set captcha
        captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': captcha.hashkey,
                     'captcha_1': captcha.response }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)

        # Call .views.login()
        login_response = views.login(request)

        # Test good printing of the page
        self.assertInHTML("Un mail est un route pour que vous puissiez confirmer la création de votre compte.",
            login_response.content.decode("utf-8"))

        # Get user and test creation in User table
        try:
            user = User.objects.get(email="test1@truc.com")
            existing_user = True
        except:
            existing_user = False
        self.assertIs(existing_user, True)

    # Add new user with different mail of existing user and test site page shown
    def test_add_new_user_with_different_mail(self):

        # Set site into Site table
        site = Site.objects.get(id=1)
        site.domain = "localhost:8000"
        site.name = "localhost"
        site.save()

        # Add existing user in database
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        # Test addition of user
        try:
            test_user = User.objects.get(email="test_user@truc.com")
            existing_test_user = True
        except:
            existing_test_user = False
        self.assertIs(existing_test_user, True)

        # Set captcha
        captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': captcha.hashkey,
                     'captcha_1': captcha.response }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)

        # Call .views.login()
        login_response = views.login(request)

        # Test good printing of the page
        self.assertInHTML("Un mail est un route pour que vous puissiez confirmer la création de votre compte.",
            login_response.content.decode("utf-8"))
        
        # Get user and test creation in User table
        try:
            user = User.objects.get(email="test1@truc.com")
            existing_user = True
        except:
            existing_user = False
        self.assertIs(existing_user, True)

    # Add new user with same mail of existing user and test site page shown
    def test_add_new_user_with_same_mail(self):

        # Set site into Site table
        site = Site.objects.get(id=1)
        site.domain = "localhost:8000"
        site.name = "localhost"
        site.save()

        # Add existing user in database
        User.objects.create_user(username="test_user", email="test1@truc.com")
        # Test addition of user
        try:
            test_user = User.objects.get(email="test1@truc.com")
            existing_test_user = True
        except:
            existing_test_user = False
        self.assertIs(existing_test_user, True)

        # Set captcha
        captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': captcha.hashkey,
                     'captcha_1': captcha.response }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)
        
        # Call .views.login()
        login_response = views.login(request)

        # Test good printing of the page
        self.assertInHTML("Un mail est un route avec un lien magique qui vous permettra de vous connecter.",
            login_response.content.decode("utf-8"))
        
    # Minimum of 2 user with the same mail in database and test site page shown
    def test_two_users_with_same_mail(self):

        # Set site into Site table
        site = Site.objects.get(id=1)
        site.domain = "localhost:8000"
        site.name = "localhost"
        site.save()

        # Add existing user in database
        User.objects.create_user(username="test_user1", email="test@truc.com")
        User.objects.create_user(username="test_user2", email="test@truc.com")
        # Test addition of user and that number of users superior to 1
        try:
            test_user_count = User.objects.count()
            test_user = User.objects.filter(email="test@truc.com")
            existing_test_user = True
        except:
            existing_test_user = False
        self.assertGreaterEqual(test_user_count, 2)
        self.assertIs(existing_test_user, True)

        # Set captcha
        captcha = CaptchaStore.objects.get(hashkey=CaptchaStore.generate_key())
        # Set parameters to similate POST
        context = { "email": "test@truc.com",
                     'captcha_0': captcha.hashkey,
                     'captcha_1': captcha.response }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)
        
        # Call .views.login()
        login_response = views.login(request)
        
        # Test printed error message
        self.assertIn(login_response.content.decode("utf-8"), "Data error: Multiple email addresses found")


class TokenMailTest(TestCase):

    # Test mail with valid token and redirection to index page
    def test_mail_with_valid_token(self):
        # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 20)
        # Test redirection to index
        index_response = self.client.get("/auth/activate/True/" + token)
        self.assertEqual(index_response.url, "/")

    # Test mail with invalid token and redirection to account_activation_invalid.html
    def test_mail_with_invalid_token(self):
        # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 20)
        # Test redirection to invalid page
        invalid_response = self.client.get("/auth/activate/True/" + token[:-2] + get_random_string(2))
        self.assertIn("Le lien de confirmation est invalide. Peut-être qu'il a déjà été utilisé ou qu'il a expiré.",
            invalid_response.content.decode("utf-8"))

    # Test already used token and redirection to account_activation_invalid.html
    def test_mail_with_used_token(self):
        # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 20)
        # Test redirection to invalid page
        response1 = self.client.get("/auth/activate/True/" + token)
        response2 = self.client.get("/auth/activate/True/" + token)
        self.assertNotEqual(response2.url, "/")
    
    # Test out of time token and redirection to account_activation_invalid.html
    def test_mail_with_timed_out_token(self):
        # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 1/60)
        sleep(2)
        # Test redirection to invalid page
        response = self.client.get("/auth/activate/True/" + token)
        self.assertInHTML("Le lien de confirmation est invalide. Peut-être qu'il a déjà été utilisé ou qu'il a expiré.",
            response.content.decode("utf-8"))


class SessionCookieTest(TestCase):

    # Test remember me checked
    def test_checked_remember_me(self):

       # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 20)
        
        # Set remember_me to "True" like if checked
        remember_me = "True"
        # Simulate connexion
        response = self.client.get("/auth/activate/" + remember_me + "/" + token)
        
        # Get cookies
        cookies = response.client.cookies
        for k, v in cookies.items():
            if k == "sessionid":
                max_age = v["max-age"]

        # Test that max-age value of sessionid cookie is set to 1 month
        self.assertEqual(max_age, 60 * 60 * 24 * 30)

    # Test remember me unchecked
    def test_unchecked_remember_me(self):

       # create user and get pk
        User.objects.create_user(username="test_user", email="test_user@truc.com")
        user = User.objects.get(username="test_user")
        
        # Create token with user.pk
        token = make_timed_token(user.pk, 20)
        
        # Set remember_me to "False" like if checked
        remember_me = "False"
        # Simulate connexion
        response = self.client.get("/auth/activate/" + remember_me + "/" + token)
        
        # Get cookies
        cookies = response.client.cookies
        for k, v in cookies.items():
            if k == "sessionid":
                max_age = v["max-age"]

        # Test that max-age value of sessionid cookie is set to expire at the end of the session
        self.assertEqual(max_age, "")
