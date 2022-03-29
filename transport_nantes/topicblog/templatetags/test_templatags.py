from django.conf import settings
from django.template import Template, Context
from django.test import TestCase
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from topicblog.models import TopicBlogItem,TopicBlogLauncher
from datetime import datetime, timezone

class TBEmailTemplateTagsTests(TestCase):

    def test_email_full_width_image(self):
        # An existing static image
        filepath = "asso_tn/belvederes.jpg"
        alt_text = "Belvederes"
        link = "https://mobilitains.fr"
        template_string = (
            "{% load static %}{% load email_tags %}"
            "{% static "f"'{filepath}'"" as filepath %}"
            "{% email_full_width_image filepath " f"'{alt_text}' '{link}'"
            " %}")
        context = Context()
        rendered_template = Template(template_string).render(context)
        # Exepcted result is from email_full_width_image's code.
        expected_template = f"""
        <tr>
            <td
            style="padding:0;font-size:24px;line-height:28px;font-weight:bold;background-color:#ffffff;">
                <a href="{link}" style="text-decoration:none;">
                    <img src="{settings.STATIC_URL}{filepath}" width="600" alt="{alt_text}"
                    style="width:100%;height:auto;display:block;border:none;text-decoration:none;color:#363636;padding-bottom:15px;">
                </a>
            </td>
        </tr>
        """.format( # noqa
            filepath=filepath,
            alt_text=alt_text,
            link=link)

        # Get rid of the whitespaces
        rendered_template = " ".join(rendered_template.split())
        expected_template = " ".join(expected_template.split())

        self.assertEqual(rendered_template, expected_template)

    def test_email_body_text_md(self):

        text = "This is a test"
        expected_template = \
            f"""
            <tr>
                <td style="padding:30px;background-color:#ffffff;">
                    <p style="margin:0;">
                        {text}
                    </p>
                </td>
            </tr>
            """
        template_string = (
            "{% load email_tags %}"
            "{% email_body_text_md text %}")
        context = Context({"text": text})
        rendered_template = Template(template_string).render(context)
        # Get rid of the whitespaces
        rendered_template = " ".join(rendered_template.split())
        expected_template = " ".join(expected_template.split())
        self.assertEqual(rendered_template, expected_template)

    def test_email_cta_button(self):

        slug = "index"
        label = "Go to the homepage"
        expected_template = """
        <tr>
            <td style="padding-right:30px;padding-left:30px;padding-bottom:15px;
            background-color:#ffffff;text-align:center;">
                <p>
                    <a href="{slug}" class="btn
                    donation-button btn-lg">
                    {label} <i class="fa fa-arrow-right" area-hidden="true"></i>
                    </a>
                </p>
            </td>
        </tr>
        """.format(
            slug=reverse_lazy("topic_blog:view_item_by_slug", args=[slug]),
            label=label
        )

        template_string = (
            "{% load email_tags %}"
            "{% email_cta_button slug label %}")
        context = Context({"slug": slug, "label": label})
        rendered_template = Template(template_string).render(context)
        # Get rid of the whitespaces
        rendered_template = " ".join(rendered_template.split())
        expected_template = " ".join(expected_template.split())

        self.assertEqual(rendered_template, expected_template)


class TBLauncherTemplateTagsTests(TestCase):

    def setUp(self):
        self.admin = \
            User.objects.create_superuser(username='test-user',
                                          password='test-pass')
        self.admin.save()
        self.item = TopicBlogItem.objects.create(
            slug="home",
            date_modified=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.admin,
            template_name="topicblog/content.html",
            body_text_1_md="body 1",
            header_image="picture.png",
            title="Test-title")
        self.item.save()
        self.launcher = TopicBlogLauncher.objects.create(
            slug="slug",
            launcher_image="picture.png",
            launcher_image_alt_text="picture",
            launcher_text_md="laucher text",
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.admin,
            article_slug=self.item.slug,
            template_name="topicblog/content_launcher.html",
            headline="Headline")
        self.launcher.save()

    def test_launcher(self):
        url = reverse_lazy("topic_blog:view_item_by_slug",
                           args=[self.launcher.article_slug])
        link = f'<a href="{url}">'
        img = self.launcher.launcher_image.url
        alt = self.launcher.launcher_image_alt_text
        image = \
            f'<img class="rounded" src="{img}" alt="{alt}" style="width:100%">'
        title = \
            f'<h3 class="font-weight-light">{ self.launcher.headline }</h3>'
        text = f'<p>{ self.launcher.launcher_text_md }</p>'
        template_string = (
            "{% load launcher %}"
            "{% launcher slug %}")
        context = Context({"slug": self.launcher.slug})
        rendered_template = Template(template_string).render(context)
        self.assertIn(link, rendered_template)
        self.assertIn(image, rendered_template)
        self.assertIn(title, rendered_template)
        self.assertIn(text, rendered_template)


class TBItemTeaserTemplateTagsTests(TestCase):

    def setUp(self):
        TBLauncherTemplateTagsTests.setUp(self)

    def test_item_teaser(self):
        url = reverse_lazy("topic_blog:view_item_by_slug",
                           args=[self.item.slug])
        link = f'<a href="{url}" class="btn donation-button btn-lg" >'
        title = \
            f'<h2 class="card-title text-white">{self.item.header_title}</h2>'
        item_description = self.item.header_description
        description = \
            f'<p class="card-text text-white">{item_description}</p>'
        text = f'<p>{ self.item.body_text_1_md}</p>'
        template_string = (
            "{% load launcher %}"
            "{% item_teaser slug %}")
        context = Context({"slug": self.launcher.slug})
        rendered_template = Template(template_string).render(context)
        self.assertIn(link, rendered_template)
        self.assertIn(title, rendered_template)
        self.assertIn(description, rendered_template)
        self.assertIn(text, rendered_template)
