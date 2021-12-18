from django.test import TestCase, Client
from topicblog.models import (TopicBlogItem, TopicBlogTemplate,
                              TopicBlogContentType)
from django.contrib.auth.models import User
from datetime import datetime, timezone


class TestOg_Twitter(TestCase):
    def setUp(self):
        # Creates a user for FKs
        self.user = User.objects.create(username='user-og-twitter',
                                        password='mdp-og-twitter')
        # Creates a base content type for FKs
        self.content_type = TopicBlogContentType.objects.create(
            content_type="test_type")
        # Create a base template for FKs
        self.template = TopicBlogTemplate.objects.create(
            template_name="topicblog/content.html",
            content_type=self.content_type)
        # Create a TopicBlog with all og value and empty twitter
        self.full_og = TopicBlogItem.objects.create(
            slug="og",
            item_sort_key=0,
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
        # Create a TopicBlog with all twitter value and  empty og
        self.full_twitter = TopicBlogItem.objects.create(
            slug="twitter",
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
            slug="both",
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
        # Create a TopicBlog with og and twitter empty value
        self.empty_both = TopicBlogItem.objects.create(
            slug="empty",
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

        c = Client()

        # create the reponse for each page
        self.reponse_og = c.get('/tb/t/og/')
        self.reponse_twitter = c.get('/tb/t/twitter/')
        self.reponse_both = c.get('/tb/t/both/')
        self.reponse_empty = c.get('/tb/t/empty/')

    # testing with all og value and empty twitter value
    def testing_og_full(self):
        og_title = "<meta property='og:title' content='Og title' />"
        self.assertContains(self.reponse_og, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Og description' />")
        self.assertContains(self.reponse_og, og_description,
                            status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/media/og_image.png' />")
        self.assertContains(self.reponse_og, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Og title' />")
        self.assertContains(self.reponse_og, twitter_title,
                            status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description'"
                               "content='Og description' />")
        self.assertContains(
            self.reponse_og, twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image'"
                         "content='/media/og_image.png' />")
        self.assertContains(self.reponse_og, twitter_image,
                            status_code=200, html=True)

    # testing with all twitter value and empty og
    def testing_twitter_full(self):
        og_title = "<meta property='og:title' content='Twitter title' />"
        self.assertContains(self.reponse_twitter, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Twitter description' />")
        self.assertContains(self.reponse_twitter,
                            og_description, status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/media/twitter_image.png' />")
        self.assertContains(self.reponse_twitter, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Twitter title' />")
        self.assertContains(self.reponse_twitter,
                            twitter_title, status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description'"
                               "content='Twitter description' />")
        self.assertContains(self.reponse_twitter,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image' "
                         "content='/media/twitter_image.png' />")
        self.assertContains(self.reponse_twitter,
                            twitter_image, status_code=200, html=True)

    # testing with twitter and og full value
    def testing_both_full(self):
        og_title = "<meta property='og:title' content='Og title' />"
        self.assertContains(self.reponse_both, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Og description' />")
        self.assertContains(self.reponse_both, og_description,
                            status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/media/og_image.png' />")
        self.assertContains(self.reponse_both, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Twitter title' />")
        self.assertContains(self.reponse_both, twitter_title,
                            status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description'"
                               "content='Twitter description' />")
        self.assertContains(self.reponse_both,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image'"
                         "content='/media/twitter_image.png' />")
        self.assertContains(self.reponse_both, twitter_image,
                            status_code=200, html=True)

    # testing with both empty but with header
    def testing_empty(self):
        og_title = ("<meta property='og:title'"
                    "content='Mobilitains - "
                    "Pour une mobilité multimodale' />")
        self.assertContains(self.reponse_empty, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Nous agissons pour une mobilité plus "
                          "fluide, plus sécurisée et plus vertueuse' />")
        self.assertContains(self.reponse_empty,
                            og_description, status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/media/image-header.png' />")
        self.assertContains(self.reponse_empty, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Mobilitains - "
                         "Pour une mobilité multimodale' />")
        self.assertContains(self.reponse_empty, twitter_title,
                            status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description'"
                               "content='Nous agissons pour une mobilité plus "
                               "fluide, plus sécurisée et plus vertueuse' />")
        self.assertContains(self.reponse_empty,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image'"
                         "content='/media/image-header.png' />")
        self.assertContains(self.reponse_empty, twitter_image,
                            status_code=200, html=True)
