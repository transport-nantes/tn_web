from django.test import TestCase, RequestFactory

from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
import authentication.views as views

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

        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': "captcha",
                     'captcha_1': "PASSED" }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)

        # Call .views.login()
        login_response = views.login(request)

        # Test good site page calling
        self.assertEqual(login_response.url, "/auth/account_activation_sent/True")

        # Get account_activation_sent page
        sent_activation_response = self.client.get(login_response.url)
        # Test good printing of the page
        self.assertInHTML("Un mél est un route pour que vous puissiez confirmer la création de votre compte.",
            sent_activation_response.content.decode("utf-8"))

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

        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': "captcha",
                     'captcha_1': "PASSED" }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)

        # Call .views.login()
        login_response = views.login(request)

        # Test good site page calling
        self.assertEqual(login_response.url, "/auth/account_activation_sent/True")

        # Get account_activation_sent page
        sent_activation_response = self.client.get(login_response.url)
        # Test good printing of the page
        self.assertInHTML("Un mél est un route pour que vous puissiez confirmer la création de votre compte.",
            sent_activation_response.content.decode("utf-8"))
        
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

        # Set parameters to similate POST
        context = { "email": "test1@truc.com",
                     'captcha_0': "captcha",
                     'captcha_1': "PASSED" }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)
        
        # Call .views.login()
        login_response = views.login(request)

        # Test good site page calling
        self.assertEqual(login_response.url, "/auth/account_activation_sent/False")

        # Get account_activation_sent page
        sent_activation_response = self.client.get(login_response.url)
        # Test good printing of the page
        self.assertInHTML("Un mél est un route avec un lien magique qui vous permettra de connecter.",
            sent_activation_response.content.decode("utf-8"))
        
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

        # Set parameters to similate POST
        context = { "email": "test@truc.com",
                     'captcha_0': "captcha",
                     'captcha_1': "PASSED" }
        request = RequestFactory().post(reverse("authentication:login"), context, follow=True)
        
        # Call .views.login()
        login_response = views.login(request)
        
        # Test printed error message
        self.assertIn(login_response.content.decode("utf-8"), "Data error: Multiple email addresses found")
