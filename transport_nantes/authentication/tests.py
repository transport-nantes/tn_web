from django.test import TestCase

from django.core import mail
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

# Create your tests here.


class PasswordResetTest(TestCase):

    def test_custom_password_reset(self):
    
        # Set site into Site table
        site = Site.objects.get(id=1)
        site.domain = "localhost:8000"
        site.name = "localhost"
        site.save()

        # Add existing user in database
        User.objects.create_user(username="test_user", email="test_user@truc.com", password="secretpwd")
        # Test addition of user
        try:
            test_user = User.objects.get(email="test_user@truc.com")
            existing_test_user = True
        except:
            existing_test_user = False
        self.assertIs(existing_test_user, True)
        
        # Post mail address in password_reset, see if redirection and mail sent
        mail_response = self.client.post(reverse("authentication:password_reset"), {"email": "test_user@truc.com"})

        # Check if password reset mail sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Transport Nantes - Réinitialisation du mot de passe")

        # Test redirection
        self.assertEqual(mail_response.url, "/auth/password_reset/done/")

        # Get token and uid to pass to url
        token = mail_response.context[0]["token"]
        uid = mail_response.context[0]["uid"]

        # Call web page from link and get redirection
        link_response = self.client.get(reverse("authentication:password_reset_confirm",
            kwargs={"token": token, "uidb64": uid}),
            )

        # Pass new password to redirected page
        reset_response = self.client.post(link_response.url,
            {"new_password1": "pwdsecret", "new_password2": "pwdsecret"},
            )
        
        # Test final redirection when password reset is done
        self.assertEqual(reset_response.url, "/auth/reset/done/")
