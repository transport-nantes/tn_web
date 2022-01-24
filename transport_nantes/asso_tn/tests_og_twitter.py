from django.test import TestCase, Client
from topicblog.models import TopicBlogItem
from django.contrib.auth.models import User
from datetime import datetime, timezone
from .templatetags.og_twitter import (get_image_url, first_not_empty,
                                      first_not_empty_image)


class Test_Og_Twitter_Dymanic_Page(TestCase):
    def setUp(self):
        # Creates a user for FKs
        self.user = User.objects.create(username='user-og-twitter',
                                        password='mdp-og-twitter')
        # Create a TopicBlog with all og value and empty twitter
        self.full_og = TopicBlogItem.objects.create(
            slug="og",
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name="topicblog/content.html",
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
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name="topicblog/content.html",
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
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name="topicblog/content.html",
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
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name="topicblog/content.html",
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
        self.reponse_legales = c.get('/tb/t/twitter/')
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
        self.assertContains(self.reponse_legales, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Twitter description' />")
        self.assertContains(self.reponse_legales,
                            og_description, status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/media/twitter_image.png' />")
        self.assertContains(self.reponse_legales, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Twitter title' />")
        self.assertContains(self.reponse_legales,
                            twitter_title, status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description'"
                               "content='Twitter description' />")
        self.assertContains(self.reponse_legales,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image' "
                         "content='/media/twitter_image.png' />")
        self.assertContains(self.reponse_legales,
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


class Test_Og_Twitter_Static_Page(TestCase):
    def setUp(self):
        c = Client()
        # create the reponse for each page
        self.reponse_legales = c.get('/l/mentions-legales')
        self.reponse_jobs = c.get('/l/jobs')

    def testing_legales(self):
        og_title = ("<meta property='og:title'"
                    "content='Mobilitains - Pour une mobilité multimodale' />")
        self.assertContains(self.reponse_legales, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Nous agissons pour une mobilité plus "
                          "fluide, plus sécurisée et plus vertueuse'/>")
        self.assertContains(self.reponse_legales,
                            og_description, status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/static/velopolitain/v1.png' />")
        self.assertContains(self.reponse_legales, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Mobilitains - "
                         "Pour une mobilité multimodale'/>")
        self.assertContains(self.reponse_legales,
                            twitter_title, status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description' "
                               "content='Nous agissons pour une mobilité plus "
                               "fluide, plus sécurisée et plus vertueuse'/>")
        self.assertContains(self.reponse_legales,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image' "
                         "content='/static/asso_tn/mobilite-pour-tous.jpg' />")
        self.assertContains(self.reponse_legales,
                            twitter_image, status_code=200, html=True)

    def testing_jobs(self):
        og_title = ("<meta property='og:title'"
                    "content='Mobilitains - Pour une mobilité multimodale' />")
        self.assertContains(self.reponse_jobs, og_title,
                            status_code=200, html=True)
        og_description = ("<meta property='og:description'"
                          "content='Nous agissons pour une mobilité plus "
                          "fluide, plus sécurisée et plus vertueuse'/>")
        self.assertContains(self.reponse_jobs,
                            og_description, status_code=200, html=True)
        og_image = ("<meta property='og:image'"
                    "content='/static/velopolitain/v1.png' />")
        self.assertContains(self.reponse_legales, og_image,
                            status_code=200, html=True)
        twitter_title = ("<meta name='twitter:title'"
                         "content='Mobilitains - "
                         "Pour une mobilité multimodale'/>")
        self.assertContains(self.reponse_jobs,
                            twitter_title, status_code=200, html=True)
        twitter_description = ("<meta name='twitter:description' "
                               "content='Nous agissons pour une mobilité plus "
                               "fluide, plus sécurisée et plus vertueuse'/>")
        self.assertContains(self.reponse_jobs,
                            twitter_description, status_code=200, html=True)
        twitter_image = ("<meta name='twitter:image' "
                         "content='/static/asso_tn/mobilite-pour-tous.jpg' />")
        self.assertContains(self.reponse_legales,
                            twitter_image, status_code=200, html=True)


class Test_template_tags_og_twitter(TestCase):
    def setUp(self):
        # Creates a user for FKs
        self.user = User.objects.create(username='template-user',
                                        password='mdp-template')
        # Create a TopicBlog with all og value and empty twitter
        self.template_tags = TopicBlogItem.objects.create(
            slug="templatetags",
            publication_date=datetime.now(timezone.utc),
            user=self.user,
            template_name="topicblog/content.html",
            title="Template Tags",
            header_image="image-header.png",
            twitter_title="",
            twitter_description="",
            twitter_image="twitter_image.png",
            og_title="",
            og_description="",
            og_image="og_image.png"
        )

    def testing_get_image_url(self):
        og_image = self.template_tags.og_image
        twitter_image = self.template_tags.twitter_image
        header_image = self.template_tags.header_image
        self.assertEqual(get_image_url("image.png"), "/static/image.png")
        self.assertEqual(get_image_url("default_image.png"),
                         "/static/default_image.png")
        self.assertEqual(get_image_url(twitter_image),
                         "/media/twitter_image.png")
        self.assertEqual(get_image_url(og_image), "/media/og_image.png")
        self.assertEqual(get_image_url(header_image),
                         "/media/image-header.png")

    def testing_first_not_empty(self):
        self.assertEqual(first_not_empty("deux", "", 0, "un"), "deux")
        self.assertEqual(first_not_empty("", "", 0, "un"), "un")
        self.assertEqual(first_not_empty("trois", "deux", 0, "un"), "trois")
        self.assertEqual(first_not_empty("un", "", 0, "", ""), "un")
        self.assertEqual(first_not_empty("", "", 0, ""), None)

    def testing_first_not_empty_image(self):
        og_image = self.template_tags.og_image
        twitter_image = self.template_tags.twitter_image
        header_image = self.template_tags.header_image
        self.assertEqual(first_not_empty_image(
            "", "", "default.png"), "/static/default.png")
        self.assertEqual(first_not_empty_image(
            "", "", header_image, "default"), "/media/image-header.png")
        self.assertEqual(first_not_empty_image(
            og_image, twitter_image, "", "default"), "/media/og_image.png")
        self.assertEqual(first_not_empty_image(
            "", twitter_image, header_image, "default"),
            "/media/twitter_image.png")
        self.assertEqual(first_not_empty_image("", "", "", ""), None)
