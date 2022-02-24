from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase
from django.urls import reverse
from mailing_list.models import MailingList
from mailing_list.events import (get_subcribed_users_email_list,
                                 unsubscribe_user_from_list,
                                 subscribe_user_to_list)

from .models import TopicBlogEmail, TopicBlogItem


class Test(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        self.user.save()
        # Create a base template
        self.template_name = "topicblog/content.html"
        # Create an Item with a slug, ID = 1
        self.main_page_slug_name = ("ligne-johanna-rolland-"
                                    "pour-plus-de-mobilite")
        self.item_with_slug = TopicBlogItem.objects.create(
            slug=self.main_page_slug_name,
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=9),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name=self.template_name,
            title="Test-title")

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TBIEditStatusCodeTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        self.user.save()
        # Create a user with all permission
        self.user_permited = User.objects.create_user(username='test-staff',
                                                      password='test-staff')
        self.user_permited.is_staff = True
        edit_permission = Permission.objects.get(codename="tbi.may_edit")
        view_permission = Permission.objects.get(codename="tbi.may_view")
        publish_permission = Permission.objects.get(codename="tbi.may_publish")
        publish_self_permission = Permission.objects.get(
            codename="tbi.may_publish_self")
        self.user_permited.user_permissions.add(
            edit_permission,
            view_permission,
            publish_permission,
            publish_self_permission
        )
        self.user_permited.save()

        self.user_permited_client = Client()
        self.unauth_client = Client()

        # login the user
        self.client.login(username='test-user', password='test-pass')
        # login the staff
        self.user_permited_client.login(
            username='test-staff', password='test-staff')

        # Create a base template
        self.template_name = "topicblog/content.html"
        # Create an Item with a slug, ID = 1
        self.item_with_slug = TopicBlogItem.objects.create(
            slug="test-slug",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=9),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.user,
            body_text_1_md="body 1",
            body_text_2_md="body 2",
            body_text_3_md="body 3",
            template_name=self.template_name,
            title="Test-title")

        # Create an Item with no slug, ID = 2
        self.item_without_slug = TopicBlogItem.objects.create(
            slug="",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=10),
            publication_date=None,
            user=self.user,
            template_name=self.template_name,
            title="Test-title")
        # Create an Item with a slug and higher publication date, ID = 3
        self.item_with_higher_date = TopicBlogItem.objects.create(
            slug="test-slug",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=7),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name=self.template_name,
            title="Test-title")
        # Create an intem with the body image but no the alt image
        self.item_without_alt = TopicBlogItem.objects.create(
            slug="test-slug-no-alt",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=7),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.user,
            body_image="body.png",
            body_text_1_md="body 1",
            body_text_2_md="body 2",
            body_text_3_md="body 3",
            template_name=self.template_name,
            title="Test-title")
        # Create an item without publication date and first publication date
        self.item_without_date = TopicBlogItem.objects.create(
            slug="test-slug-no-date",
            date_modified=datetime.now(timezone.utc) - timedelta(seconds=7),
            user=self.user,
            body_text_1_md="body 1",
            body_text_2_md="body 2",
            body_text_3_md="body 3",
            template_name=self.template_name,
            title="Test-title")

    def test_item_with_slug_edit(self):
        """ Test status codes for the edit page of an item with a slug
        The edition page is accessed through the TopicBlogItemEdit view.
        In this test we will use these items from the setUp:
            - An item with a slug, ID = 1, date_modified = 1
            - An item with a slug and higher publish date, ID = 3,
              date_modified = 3
        We aim to check that we get the correct status codes on the edition
        page in various situations involving items with a slug.
        Items which have a saved slug edition page MUST return 200 if:
            - An existing slug is provided. In this case it loads the
              item with the publication date.
            OR
            - The provided slug and ID are matching the pair of slug
              and ID of an item. In this case it loads the item
              corresponding to this slug/id pair.
        Edition page MUST return 404 if:
            - The slug provided doesn't match any existing item's slug.
              In this case it raises a 404.
            - The slug / id pair provided doesn't match any existing item.
              In this case it raises a 404.
            - No slug is provided.

        Whith unauthenticated users, edition page MUST always return a 404
        or 302 (redirection to login)

        Whith authenticated users, edition page MUST always return a 203
        or 403.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't access this page."
                    f"\nitem with slug: {self.item_with_slug}"
                    f"\nkwargs: {self.item_with_slug.id}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 if not auth"
                    f"\nitem with slug: {self.item_with_slug}"
                    f"\nkwargs: {self.item_with_slug.id}"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page should return 404 if we don't provide "
                    "the slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"
                    f"\nkwargs: {self.item_with_slug.id}"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:edit_item_by_pkid",
                        kwargs={
                            "pkid": self.item_with_slug.id
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        users_expected_1 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even if we provide "
                    "the slug associated with the item but not auth."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:edit_item",
                        kwargs={
                            "pkid": self.item_with_slug.id,
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        users_expected_2 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even if we provide "
                    "the slug associated with the item but not auth."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "wrong slug and id associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:edit_item",
                        kwargs={
                            "pkid": 999999999,
                            "the_slug": "wrong-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        users_expected_3 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 if we provide the "
                    "wrong slug and id associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "correct slug but wrong id associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_3:
            response = user_type["client"].get(
                reverse("topicblog:edit_item",
                        kwargs={
                            "pkid": 999999999,
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        users_expected_4 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page MUST return 302 even if we provide the "
                    "wrong slug and correct id associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "wrong slug and correct id associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_4:
            response = user_type["client"].get(
                reverse("topicblog:edit_item",
                        kwargs={
                            "pkid": self.item_with_slug.id,
                            "the_slug": "wrong-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # Edit with only the correct slug.
        # Checks it loads the greatest modification date.

        latest_date_modified = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
        ).order_by("date_modified").last().date_modified

        users_expected_5 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even if we provide "
                    "the correct slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "correct slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_5:
            response = user_type["client"].get(
                reverse("topicblog:edit_item_by_slug",
                        kwargs={
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        self.assertEqual(latest_date_modified,
                         self.item_with_higher_date.date_modified,
                         msg="The page MUST load the item with the latest "
                         "date modified."
                         f"\nitem with slug: {self.item_with_slug}"
                         f"\nHighest date_modified: {latest_date_modified}")

    def test_item_without_slug_edit(self):
        """Test status code of edit page of items without slug
        The edition page is accessed through the TopicBlogItemEdit view.
        In this test we will use these items from the setUp:
            - An item without a slug, ID = 2, date_modified = 0
        We aim to check that we get the correct status codes on the edition
        page in various situations involving items without a slug.
        For Items which don't have a saved slug edition page
        MUST return 200 if:
            - Only an existing PK ID is provided, and the item corresponding
            to that ID doesn't have a slug, or an empty one. In this case it
            loads the item with the corresponding PK ID.
        Edition page MUST NOT return 200 if:
            - The PK ID provided doesn't match any existing item's PK ID.
            In this case it raises a 404.
            - Only a PK ID is provided and matches an item with a slug.
            In this case it raises a 404.

        Whith unauthenticated users, edition page MUST always return a 404
        or 302 (redirection to login)

        Whith authenticated users, edition page MUST always return a 203
        or 403.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even if we don't "
                    "provide a slug and the item does not have one."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we don't provide "
                    "a slug and the item does not have one."},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:edit_item_by_pkid",
                        kwargs={
                            "pkid": self.item_without_slug.id
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        users_expected_1 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't edit items."},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 if we provide the "
                    "correct id but the item does not have a slug and"
                    "we're not auth"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "correct id but the item does not have a slug."},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:edit_item",
                        kwargs={
                            "pkid": self.item_without_slug.id,
                            "the_slug": "test-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_item_creation_status_code(self):
        """
        Test the creation form status code

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't create items"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 if not auth"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we don't provide any arg"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(reverse("topicblog:new_item"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])


class TBIViewStatusCodeTests(TestCase):
    """
    Test the status code of the TopicBlogItemView
    For this test we use a list of dictionaries, that is composed of:
        - client = the client of user (auth user, unauth and staff user)
        - code = the statut code that should return for this user (varie)
        - message = the error message (varie)
    """

    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)

    def test_item_with_slug_view(self):
        """
        Test the status code of items with a slug in
        the TopicBlogItemView.

        In this test we will use these items from the setUp:
            - An item with a slug, ID = 1, date_modified = now - 5
            - An item with a slug and  key, ID = 3

        We aim to check that we get the correct status codes on the view
        page in various situations involving items with a slug.

        For items which have a slug view page MUST return 200 if:
            - You provide a slug and an item corresponding to that slug exists.
            In this case it loads the item with the corresponding slug and
            highest publish date.
            - You're connected and provide both an ID/slug pair corresponding
            to an existing item. In this case it loads the corresponding item.

        View page MUST NOT return 200 if:
            - You provide a slug but no item corresponding to that slug exists.
            In this case it raises a 404.
            - You provide an ID but you're not logged in.
            - You provide an ID but no item corresponding to that ID exists.
            In this case it raises a 404.
            - You provide only the ID while the item does have a slug.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        # ##### view_item_by_pkid ######

        # View with correct slug and correct id
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "correct slug and id associated with the item."},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid",
                        kwargs={
                            "pkid": self.item_with_slug.id,
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # View with wrong slug and correct id
        users_expected_1 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "wrong slug and correct id associated with the item."},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid",
                        kwargs={
                            "pkid": self.item_with_slug.id,
                            "the_slug": "wrong-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # View with correct slug and wrong id
        users_expected_2 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "correct slug but wrong id associated with the item."},
        ]
        for user_type in users_expected_2:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid",
                        kwargs={
                            "pkid": 999999,
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # View with wrong slug and wrong id
        users_expected_3 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "wrong slug and wrong id associated with the item."},
        ]
        for user_type in users_expected_3:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid",
                        kwargs={
                            "pkid": 999999,
                            "the_slug": "wrong-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # ###### view_item_by_pkid_only ######

        # View with correct id
        users_expected_4 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "correct id associated with the item but the item "
                    "does have a slug."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_4:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid_only",
                        kwargs={
                            "pkid": self.item_with_slug.id
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # View with wrong id
        users_expected_5 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "wrong id associated with the item but the item "
                    "does have a slug."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_5:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid_only",
                        kwargs={
                            "pkid": 999999
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # ##### view_item_by_slug ######

        # View with correct slug
        users_expected_6 = [
            {"client": self.client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "correct slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.unauth_client, "code": 200,
             "msg": "The page should return 200 if we provide the "
                    "correct slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "correct slug associated with the item."
                    f"\nitem with slug: {self.item_with_slug}"},
        ]
        for user_type in users_expected_6:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_slug",
                        kwargs={
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        latest_date_modified = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
        ).order_by("date_modified").last()

        self.assertEqual(response.context["page"],
                         latest_date_modified,
                         msg="The page MUST load the item with the highest "
                         "date_modified."
                         f"\nitem with slug: {self.item_with_slug}"
                         f"\nhighest date_modified: {latest_date_modified}")

        # View with wrong slug
        users_expected_7 = [
            {"client": self.client, "code": 404,
             "msg": "The page MUST return 404 if we provide a "
                    "wrong slug not related to any item."},
            {"client": self.unauth_client, "code": 404,
             "msg": "The page should return 404 if we provide a "
                    "wrong slug not related to any item."},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide a "
                    "wrong slug not related to any item."},
        ]
        for user_type in users_expected_7:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_slug",
                        kwargs={
                            "the_slug": "wrong-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_item_without_slug_view(self):
        """
        Test the status code of items without a slug in
        the TopicBlogItemView.

        In this test we will use this item from the setUp:
            - An item without a slug, ID = 2, date_modified = 0

        We aim to check that we get the correct status codes on the view
        page in various situations involving items without a slug.

        For items which do not have a slug view page MUST return 200 if:
            - You're connected and only provide an existing ID. In this case
            it loads the corresponding item.

        View page MUST NOT return 200 if:
            - You're not connected. Non logged users can't see items without
            slugs.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """

        # #### view_item_by_pkid ######

        # View with correct id but bad slug
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 404,
             "msg": "The page MUST return 404 if we provide the "
                    "correct id associated with the item but the item "
                    "does not have a slug."
                    f"\nitem without slug: {self.item_without_slug}"},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid",
                        kwargs={
                            "pkid": self.item_without_slug.id,
                            "the_slug": "a-slug"
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # #### view_item_by_pkid_only ######

        # View with correct id
        users_expected_1 = [
            {"client": self.client, "code": 403,
             "msg": "The page MUST return 403 to normal users."},
            {"client": self.unauth_client, "code": 302,
             "msg": "This page redirects to login for unauth users"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide the "
                    "correct id associated with the item and the item "
                    "does not have a slug."
                    f"\nitem without slug: {self.item_without_slug}"},
        ]
        for user_type in users_expected_1:
            response = user_type["client"].get(
                reverse("topicblog:view_item_by_pkid_only",
                        kwargs={
                            "pkid": self.item_without_slug.id
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])


class TBIListStatusCodeTests(TestCase):
    """
    Test the status code of the TopicBlogItemList view

    Normal users can't acces list pages.
    """

    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)

    def test_full_list_display(self):
        """
        Test the status code of the TopicBlogItemList view
        when the list is displayed with all items.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't view the list of items"},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even"
                    "if we provide no parameters"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide no parameters."},
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(reverse("topicblog:list_items"))
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # Checks that the number of items displayed is equal to the
        # number of TBItems with non-empty slugs.  Note that this test
        # will fail the day we implement pagination on the TBItem list
        # page.
        number_of_items = TopicBlogItem.objects.exclude(slug="").count()
        self.assertEqual(len(response.context["object_list"]),
                         number_of_items,
                         msg="The list of items MUST be the same length as "
                         "the number of items in the database."
                         f"\nnumber of items: {number_of_items}"
                         "\nnumber of items in the list: "
                         f"{len(response.context['object_list'])}")

    def test_full_list_display_with_slug(self):
        """
        Test the status code of the TopicBlogItemList view
        when the list is displayed with all items corresponding to
        a given slug.

        For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code that should return for this user (varie)
            - message = the error message (varie)
        """
        users_expected_0 = [
            {"client": self.client, "code": 403,
             "msg": "Normal users can't see the list of items."},
            {"client": self.unauth_client, "code": 302,
             "msg": "The page should return 302 even if we provide a "
                    "slug attached to an existing item."},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page MUST return 200 if we provide a "
                    "slug attached to an existing item."}
        ]
        for user_type in users_expected_0:
            response = user_type["client"].get(
                reverse("topicblog:list_items_by_slug",
                        kwargs={
                            "the_slug": self.item_with_slug.slug
                        })
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # Checks that the number of items displayed is correct
        # All items with the given slug MUST be in the context
        number_of_items = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
        ).count()

        self.assertEqual(len(response.context["object_list"]),
                         number_of_items,
                         msg="The list of items MUST be the same length as "
                         "the number of items with the corresponding slug "
                         "in the database."
                         f"\nnumber of items: {number_of_items}"
                         "\nnumber of items in the list: "
                         f'{len(response.context["object_list"])}')


class TBIModel(TestCase):
    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)

    def test_is_pubichable_function(self):
        self.assertTrue(self.item_with_slug.is_publishable())
        self.assertTrue(self.item_without_date.is_publishable())
        self.assertFalse(self.item_without_slug.is_publishable())
        self.assertFalse(self.item_without_alt.is_publishable())

    def test_publish_function(self):
        self.assertTrue(self.item_with_slug.publish())
        self.assertTrue(self.item_without_date.publish())
        self.assertFalse(self.item_without_slug.publish())
        self.assertFalse(self.item_without_alt.publish())

    def test_get_servable_status(self):
        self.assertTrue(self.item_with_slug.get_servable_status())
        self.assertFalse(self.item_without_slug.get_servable_status())
        self.assertFalse(self.item_without_date.get_servable_status())

    def test_get_image_fields_function(self):
        self.assertEqual(self.item_with_slug.get_image_fields(),
                         ['header_image', 'twitter_image',
                          'og_image', 'body_image'])
        self.assertEqual(self.item_without_slug.get_image_fields(),
                         ['header_image', 'twitter_image',
                          'og_image', 'body_image'])

    def test_get_absolute_url_function(self):
        self.assertEqual(self.item_with_slug.get_absolute_url(),
                         '/tb/admin/t/view/1/test-slug/')
        self.assertEqual(
            self.item_without_slug.get_absolute_url(), '/tb/admin/t/view/2/')

    def test_get_missing_publication_field_names(self):
        self.assertEqual(
            self.item_with_slug.get_missing_publication_field_names(), set())
        self.assertEqual(
            self.item_without_slug.get_missing_publication_field_names(),
            {'body_text_2_md', 'body_text_3_md', 'body_text_1_md', 'slug'})
        self.assertEqual(
            self.item_without_alt.get_missing_publication_field_names(),
            {'body_image', 'body_image_alt_text'})


class TBIView(TestCase):
    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)
        """For this test we use a list of dictionaries, that is composed of:
            - client = the client of user (auth user, unauth and staff user)
            - code = the statut code (not varie for user)
            - message = the error message (not varie for user)"""

        self.users_expected = [
            {"client": self.client, "code": 403,
             "msg": "User with no staff status is not permited"},
            {"client": self.unauth_client, "code": 403,
             "msg": "Unauth can't have acces to this data"},
            {"client": self.user_permited_client, "code": 200,
             "msg": "The page must return 200 the user is staff"}
        ]

    def test_get_slug_suggestions(self):
        for user_type in self.users_expected:
            response = user_type["client"].get(
                f"{reverse('topicblog:get_slug_suggestions')}"
                "?partial_slug=alt"
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # test the result of the staff user
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             ['test-slug-no-alt'])

    def test_get_slug_dict(self):
        for user_type in self.users_expected:
            response = user_type["client"].get(
                reverse('topicblog:get_slug_dict')
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

        # test the result of the staff user
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"": 1, "test-slug": 2, "test-slug-no-alt": 1,
                              "test-slug-no-date": 1, })

    def test_get_url_list(self):
        for user_type in self.users_expected:
            response = user_type["client"].get(
                f"{reverse('topicblog:get_url_list')}"
                "?slug=test-slug-no-alt"
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])
        # test the result of the staff user
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"url": "/tb/admin/t/list/test-slug-no-alt/"})


class TopicBlogEmailTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="test_user",
            email="admin@admin.com",
            password="test_password")
        self.email_article = TopicBlogEmail.objects.create(
            subject="Test subject",
            user=self.superuser,
            body_text_1_md="Test body text 1",
            slug="test-email",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            template_name="topicblog/TBEmail/email.html",
            title="Test title")
        self.mailing_list = MailingList.objects.create(
            mailing_list_name="the_mailing_list_name",
            mailing_list_token="the_mailing_list_token",
            contact_frequency_weeks=12,
            list_active=True)
        self.no_permissions_user = User.objects.create_user(
            username="user_without_permissions",
            email="test@test.com"
        )
        subscribe_user_to_list(self.superuser, self.mailing_list)
        subscribe_user_to_list(self.no_permissions_user, self.mailing_list)
        self.no_permissions_client = Client()
        self.admin_client = Client()
        self.admin_client.force_login(self.superuser)
        self.no_permissions_client.force_login(self.no_permissions_user)

        # Anonymous users are invited tol og in and from there, you
        # land either on 403 Forbidden or 200 OK depending on the
        # user's permissions.
        self.perm_needed_responses = [
            {"client": self.client, "code": 302,
             "msg": "Anonymous users are redirected to login."},
            {"client": self.no_permissions_client, "code": 403,
             "msg": ("Logged in users without proper permissions can't have "
                     "access to this page.")},
            {"client": self.admin_client, "code": 200,
             "msg": "The page must return 200 the user has the permission."}
        ]
        self.no_perm_needed_responses = [
            {"client": self.client, "code": 200,
             "msg": "The page must return 200 independently of permissions."},
            {"client": self.no_permissions_client, "code": 200,
             "msg": "The page must return 200 independently of permissions."},
            {"client": self.admin_client, "code": 200,
             "msg": "The page must return 200 independently of permissions."}
        ]

    def test_TBE_view_one_status_code(self):

        for user_type in self.perm_needed_responses:
            response = user_type["client"].get(
                reverse('topic_blog:view_email_by_pkid',
                        args=[self.email_article.pk, self.email_article.slug]
                        )
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_TBE_view_status_code(self):
        for user_type in self.no_perm_needed_responses:
            response = user_type["client"].get(
                reverse('topic_blog:view_email_by_slug',
                        args=[self.email_article.slug]
                        )
            )
            self.assertEqual(response.status_code,
                             user_type["code"], msg=user_type["msg"])

    def test_get_subcribed_users_email_list(self):

        # superuser and no_perm_user are subscribed to the mailing list
        # in the setUp method
        number_of_subscribed_users = 2
        self.assertEqual(
            len(get_subcribed_users_email_list(self.mailing_list)),
            number_of_subscribed_users)

        unsubscribe_user_from_list(self.superuser, self.mailing_list)
        number_of_subscribed_users = 1
        self.assertEqual(
            len(get_subcribed_users_email_list(self.mailing_list)),
            number_of_subscribed_users)
