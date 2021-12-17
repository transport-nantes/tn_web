from django.test import TestCase
from .models import (TopicBlogItem, TopicBlogTemplate,
                     TopicBlogContentType)
from django.contrib.auth.models import User
from datetime import datetime, timezone


class Og_Twitter(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='user-og-twitter',
                                        password='mdp-og-twitter')
        # Creates a base content type for FKs
        self.content_type = TopicBlogContentType.objects.create(
            content_type="test_type")
        # Create a base template
        self.template = TopicBlogTemplate.objects.create(
            template_name="test.html",
            content_type=self.content_type)
        # Create a TopicBlog with all og value
        self.full_og = TopicBlogItem.objects.create(
            slug="",
            item_sort_key=1,
            servable=True,
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            content_type=self.content_type,
            template=self.template,
            title="Og full",
            header_image="image-header.png",
            twitter_title="",
            twitter_description="",
            twitter_image="",
            og_title="Og title",
            og_description="Og description",
            og_image="og_image.png"
        )
        # Create a TopicBlog with all twitter value
        self.full_twitter = TopicBlogItem.objects.create(
            slug="",
            item_sort_key=1,
            servable=True,
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            content_type=self.content_type,
            template=self.template,
            title="Twitter Full",
            header_image="image-header.png",
            twitter_title="Twitter title",
            twitter_description="Twitter description",
            twitter_image="twitter_image.png",
            og_title="",
            og_description="",
            og_image=""
        )
        # Create a TopicBlog with all twitter and og value
        self.full_both = TopicBlogItem.objects.create(
            slug="",
            item_sort_key=1,
            servable=True,
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            content_type=self.content_type,
            template=self.template,
            title="Both Full",
            header_image="image-header.png",
            twitter_title="Twitter title",
            twitter_description="Twitter description",
            twitter_image="twitter_image.png",
            og_title="Og title",
            og_description="Og description",
            og_image="og_image.png"
        )
        self.empty_both = TopicBlogItem.objects.create(
            slug="",
            item_sort_key=1,
            servable=True,
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            content_type=self.content_type,
            template=self.template,
            title="Empty Full",
            header_image="image-header.png",
            twitter_title="",
            twitter_description="",
            twitter_image="",
            og_title="",
            og_description="",
            og_image=""
        )

    def test_twitter_og(self):
        # Testing when all og as a value and all twitter is empty
        test_dico_og = self.full_og.set_social_context(dict())['social']
        test_dico_og_image = test_dico_og.pop("og_image")
        test_dico_twitter_image = test_dico_og.pop("twitter_image")
        good_dico_og = {'twitter_title': 'Og title',
                        'twitter_description': 'Og description',
                        'og_title': 'Og title',
                        'og_description': 'Og description'}
        good_picture_og = "og_image.png"
        self.assertEqual(test_dico_og, good_dico_og)
        self.assertEqual(test_dico_og_image, good_picture_og)
        self.assertEqual(test_dico_twitter_image, good_picture_og)

        # Testing when all twitter as a value and all og is empty
        test_dico_twitter = self.full_twitter.set_social_context(dict())[
            'social']
        test_dico_og_image = test_dico_twitter.pop("og_image")
        test_dico_twitter_image = test_dico_twitter.pop("twitter_image")
        good_dico_twitter = {'twitter_title': 'Twitter title',
                             'twitter_description': 'Twitter description',
                             'og_title': 'Twitter title',
                             'og_description': 'Twitter description'}
        good_picture_twitter = "twitter_image.png"
        self.assertEqual(test_dico_twitter, good_dico_twitter)
        self.assertEqual(test_dico_og_image, good_picture_twitter)
        self.assertEqual(test_dico_twitter_image, good_picture_twitter)

        # Testing when og and twitter as no empty value
        test_dico_both = self.full_both.set_social_context(dict())['social']
        test_dico_og_image = test_dico_both.pop("og_image")
        test_dico_twitter_image = test_dico_both.pop("twitter_image")
        good_dico_both = {'twitter_title': 'Twitter title',
                          'twitter_description': 'Twitter description',
                          'og_title': 'Og title',
                          'og_description': 'Og description'}
        good_picture_both_twitter = "twitter_image.png"
        good_picture_both_og = "og_image.png"
        self.assertEqual(test_dico_both, good_dico_both)
        self.assertEqual(test_dico_og_image, good_picture_both_og)
        self.assertEqual(test_dico_twitter_image, good_picture_both_twitter)

        # Testing when og and twitter is empty both image take header image
        test_dico_empty = self.empty_both.set_social_context(dict())['social']
        test_dico_og_image = test_dico_empty.pop("og_image")
        test_dico_twitter_image = test_dico_empty.pop("twitter_image")
        good_dico_empty = {'twitter_title': '',
                           'twitter_description': '',
                           'og_title': '',
                           'og_description': ''}
        good_picture_empty = "image-header.png"
        self.assertEqual(test_dico_empty, good_dico_empty)
        self.assertEqual(test_dico_og_image, good_picture_empty)
        self.assertEqual(test_dico_twitter_image, good_picture_empty)
