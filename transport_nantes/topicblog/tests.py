from django.test import TestCase
from .models import TopicBlogPage, TopicBlogItem, TopicBlogTemplate
from django.contrib.auth.models import User
from django.urls import reverse


# Create your tests here.
class SimpleTest(TestCase):

    def test_main_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 404)

        TopicBlogPage.objects.create(title="test", slug="test", topic="index", template="topicblog/2020_index.html")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class TBIEditStatusCodeTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='test-user',
                                             password='test-pass')
        # Create a base template
        self.template = TopicBlogTemplate.objects.create(
            template_name="topicblog/content.html")
        # Create an Item with a slug, ID = 1
        self.item_with_slug = TopicBlogItem.objects.create(
            slug="test-slug",
            item_sort_key=1,
            servable=True,
            published=True,
            user=self.user,
            template=self.template,
            title="Test-title")
        # Create an Item with no slug, ID = 2
        self.item_without_slug = TopicBlogItem.objects.create(
            slug="",
            item_sort_key=0,
            servable=False,
            published=False,
            user=self.user,
            template=self.template,
            title="Test-title")
        # Create an Item with a slug and higher sort key, ID = 3
        self.item_with_higher_sort_key = TopicBlogItem.objects.create(
            slug="test-slug",
            item_sort_key=3,
            servable=True,
            published=True,
            user=self.user,
            template=self.template,
            title="Test-title")

    def test_item_with_slug_edit_status_code(self):
        """
        Test status codes for the edit page of an item with a slug
        """

        # Edit wihout slug given
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item_no_slug",
                    kwargs={
                        "pkid": self.item_with_slug.id
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we don't provide "
                         "the slug associated with the item."
                         f"\nitem with slug : {self.item_with_slug}"
                         f"\nkwargs : {self.item_with_slug.id}")

        # Edit with correct slug and id
        # Should return 200
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "item_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 200,
                         msg="The page should return 200 if we provide the "
                         "slug associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with wrong slug and wrong id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": 999999999,
                        "item_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we provide the "
                         "wrong slug and id associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with correct slug and wrong id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": 999999999,
                        "item_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we provide the "
                         "correct slug but wrong id associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with wrong slug and correct id
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_with_slug.id,
                        "item_slug": "wrong-slug"
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we provide the "
                         "wrong slug and correct id associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        # Edit with only the correct slug.
        # Checks it loads the highest sort key
        # Should return 200
        highest_item_sort_key = TopicBlogItem.objects.filter(
            slug=self.item_with_slug.slug
            ).order_by("item_sort_key").last().item_sort_key

        response = self.client.get(
            reverse("topicblog:edit_item_slug",
                    kwargs={
                        "item_slug": self.item_with_slug.slug
                    })
            )
        self.assertEqual(response.status_code, 200,
                         msg="The page should return 200 if we provide the "
                         "correct slug associated with the item."
                         f"\nitem with slug : {self.item_with_slug}")

        self.assertEqual(highest_item_sort_key,
                         self.item_with_higher_sort_key.item_sort_key,
                         msg="The page should load the item with the highest "
                         "sort key."
                         f"\nitem with slug : {self.item_with_slug}"
                         f"\nHighest item sort key: {highest_item_sort_key}")

    def test_item_without_slug_edit_status_code(self):
        """
        Test status code of edit page of items without slug
        """

        # Edit wihout slug given
        # Should return 200
        response = self.client.get(
            reverse("topicblog:edit_item_no_slug",
                    kwargs={
                        "pkid": self.item_without_slug.id
                    })
            )
        self.assertEqual(response.status_code, 200,
                         msg="The page should return 200 if we don't provide "
                         "a slug and the item does not have one.")

        # Edit with correct id and a slug
        # Should return 404
        response = self.client.get(
            reverse("topicblog:edit_item",
                    kwargs={
                        "pkid": self.item_without_slug.id,
                        "item_slug": "test-slug"
                    })
            )
        self.assertEqual(response.status_code, 404,
                         msg="The page should return 404 if we provide the "
                         "correct id but the item does not have a slug.")

    def test_item_creation_status_code(self):
        """
        Test the creation form status code
        """

        response = self.client.get(
            reverse("topicblog:new_item")
        )
        self.assertEqual(response.status_code, 200,
                         msg="The page should return 200 if we don't provide "
                         "any arg")
