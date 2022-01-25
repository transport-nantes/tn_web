from datetime import datetime, timedelta, timezone

from django.test import TestCase
from .models import (TopicBlogItem, TopicBlogTemplate)
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class SimpleTest(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        self.user.save()
        # Create a base template
        self.template = TopicBlogTemplate.objects.create(
            template_name="topicblog/content.html",)
        # Create an Item with a slug, ID = 1
        self.item_with_slug = TopicBlogItem.objects.create(
            slug="index",
            date_modified=datetime.now(timezone.utc) - timedelta(9),
            first_publication_date=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template=self.template,
            title="Test-title")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TBIEditStatusCodeTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        self.user.save()
        # Create a base template
        self.template = TopicBlogTemplate.objects.create(
            template_name="topicblog/content.html",)
        # Create an Item with a slug, ID = 1
        self.item_with_slug = TopicBlogItem.objects.create(
            slug="test-slug",
            date_modified=datetime.now(timezone.utc) - timedelta(9),
            first_publication_date=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template=self.template,
            title="Test-title")
        # Create an Item with no slug, ID = 2
        self.item_without_slug = TopicBlogItem.objects.create(
            slug="",
            date_modified=datetime.now(timezone.utc) - timedelta(10),
            first_publication_date=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template=self.template,
            title="Test-title")
        # Create an Item with a slug and higher sort key, ID = 3
        self.item_with_higher_sort_key = TopicBlogItem.objects.create(
            slug="test-slug",
            date_modified=datetime.now(timezone.utc) - timedelta(7),
            first_publication_date=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template=self.template,
            title="Test-title")

    def test_item_with_slug_edit(self):
        """
        Test status codes for the edit page of an item with a slug
        The edition page is accessed through the TopicBlogItemEdit view.

        In this test we will use these items from the setUp :
            - An item with a slug, ID = 1, date_modified = 1
            - An item with a slug and higher sort key, ID = 3,
            date_modified = 3

        We aim to check that we get the correct status codes on the edition
        page in various situations involving items with a slug.

        Whith unauthenticated users, edition page must always return a 404
        or 302 (redirection to login)

        """

        # Edit wihout slug given
        # Should return 302
        response = self.client.get(
            reverse("topicblog:edit_item_by_pkid",
                    kwargs={
                        "pkid": self.item_with_slug.id
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 if not auth"
                         f"\nitem with slug : {self.item_with_slug}"
                         f"\nkwargs : {self.item_with_slug.id}")

        # Edit with correct slug and id
        # Should return 302
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we provide "
                         "the slug associated with the item but not auth."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with wrong slug and wrong id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 if we provide the "
                         "wrong slug and id associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with correct slug and wrong id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": 999999999,
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we provide "
                         "the correct slug but wrong id associated with the "
                         "item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with wrong slug and correct id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "the_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page must return 302 even if we provide the "
                         "wrong slug and correct id associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with only the correct slug.
        # Should return 404
        latest_date_modified = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
            ).order_by("date_modified").last().date_modified

        response = self.client.get(
            reverse("topicblog:edit_item_by_slug",
                    kwargs={
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we provide "
                         "the correct slug associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        self.assertEqual(latest_date_modified,
                         self.item_with_higher_sort_key.date_modified,
                         msg="The page should load the item with the latest "
                         "sort key."
                         f"\nitem with slug : {self.item_with_slug}"
                         f"\nLatest item sort key: {latest_date_modified}")

    def test_item_without_slug_edit(self):
        """
        Test status code of edit page of items without slug
        The edition page is accessed through the TopicBlogItemEdit view.

        In this test we will use these items from the setUp :
            - An item without a slug, ID = 2, date_modified = 0

        We aim to check that we get the correct status codes on the edition
        page in various situations involving items without a slug.

        For Items which don't have a saved slug edition page must only
        return 200 if :

            - Only an existing PK ID is provided, and the item corresponding
            to that ID doesn't have a slug, or an empty one. In this case it
            loads the item with the corresponding PK ID.

        Edition page must NOT return 200 if :
            - The PK ID provided doesn't match any existing item's PK ID.
            In this case it raises a 404.
            - Only a PK ID is provided and matches an item with a slug.
            In this case it raises a 404.
        """

        # Edit wihout slug given
        # Should return 302
        response = self.client.get(
            reverse("topicblog:edit_item_by_pkid",
                    kwargs={
                        "pkid": self.item_without_slug.id
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we don't "
                         "provide a slug and the item does not have one.")

        # Edit with correct id and a slug
        # Should return 302
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_without_slug.id,
                        "the_slug": "test-slug"
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 if we provide the "
                         "correct id but the item does not have a slug and"
                         "we're not auth")

    def test_item_creation_status_code(self):
        """
        Test the creation form status code
        """

        response = self.client.get(
            reverse("topicblog:new_item")
        )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 if not auth")


class TBIViewStatusCodeTests(TestCase):
    """
    Test the status code of the TopicBlogItemView
    """

    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)

    def test_item_with_slug_view(self):
        """
        Test the status code of items with a slug in
        the TopicBlogItemView.

        In this test we will use these items from the setUp :
            - An item with a slug, ID = 1, date_modified = 1
            - An item with a slug and higher sort key, ID = 3,
            date_modified = 3

        We aim to check that we get the correct status codes on the view
        page in various situations involving items with a slug.

        For items which have a slug view page must only return 200 if :
            - You provide a slug and an item corresponding to that slug exists.
            In this case it loads the item with the corresponding slug and
            latest modification date.
            - You're connected and provide both an ID/slug pair corresponding
            to an existing item. In this case it loads the corresponding item.

        View page must NOT return 200 if :
            - You provide a slug but no item corresponding to that slug exists.
            In this case it raises a 404.
            - You provide an ID but you're not logged in.
            - You provide an ID but no item corresponding to that ID exists.
            In this case it raises a 404.
            - You provide only the ID while the item does have a slug.

        """
        # ##### view_item_by_pkid ######

        # View with correct slug and correct id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # View with wrong slug and correct id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "the_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # View with correct slug and wrong id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": 999999,
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # View with wrong slug and wrong id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": 999999,
                        "the_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # ###### view_item_by_pkid_only ######

        # View with correct id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid_only",
                    kwargs={
                        "pkid": self.item_with_slug.id
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # View with wrong id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid_only",
                    kwargs={
                        "pkid": 999999,
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # ##### view_item_by_slug ######

        # View with correct slug
        response = self.client.get(
            reverse("topicblog:view_item_by_slug",
                    kwargs={
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 200,
                         msg="The page should return 200 if we provide the "
                         "correct slug associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        latest_date_modified = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
            ).order_by("date_modified").last()

        self.assertEqual(response.context["page"],
                         latest_date_modified,
                         msg="The page should load the item with the latest "
                         "date_modified."
                         f"\nitem with slug : {self.item_with_slug}"
                         f"\nlatest date_modified : {latest_date_modified}")

        # View with wrong slug
        response = self.client.get(
            reverse("topicblog:view_item_by_slug",
                    kwargs={
                        "the_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we provide a "
                         "wrong slug not related to any item.")

    def test_item_without_slug_view(self):
        """
        Test the status code of items without a slug in
        the TopicBlogItemView.

        In this test we will use this item from the setUp :
            - An item without a slug, ID = 2, date_modified = 0

        We aim to check that we get the correct status codes on the view
        page in various situations involving items without a slug.

        For items which do not have a slug view page must only return 200 if :
            - You're connected and only provide an existing ID. In this case
            it loads the corresponding item.

        View page must NOT return 200 if :
            - You're not connected. Non logged users can't see items without
            slugs.
        """

        # #### view_item_by_pkid ######

        # View with correct id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid",
                    kwargs={
                        "pkid": self.item_without_slug.id,
                        "the_slug": "a-slug"
                    })
            )

        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")

        # #### view_item_by_pkid_only ######

        # View with correct id
        response = self.client.get(
            reverse("topicblog:view_item_by_pkid_only",
                    kwargs={
                        "pkid": self.item_without_slug.id
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="This page redirects to login for unauth users")


class TBIListStatusCodeTests(TestCase):
    """
    Test the status code of the TopicBlogItemList view
    With Unauth users, this view must return 302.
    """
    def setUp(self):
        TBIEditStatusCodeTest.setUp(self)

    def test_full_list_display(self):
        """
        Test the status code of the TopicBlogItemList view
        when the list is displayed with all items.
        """
        response = self.client.get(reverse("topicblog:list_items"))
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we provide no"
                         " parameters.")

    def test_full_list_display_with_slug(self):
        """
        Test the status code of the TopicBlogItemList view
        when the list is displayed with all items corresponding to
        a given slug.
        """
        response = self.client.get(
            reverse("topicblog:list_items_by_slug",
                    kwargs={
                        "the_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 302,
                         msg="The page should return 302 even if we provide a "
                         "slug attached to an existing item.")
