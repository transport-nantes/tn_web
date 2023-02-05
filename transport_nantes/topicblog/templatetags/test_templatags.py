from urllib.parse import quote
from django.http import HttpRequest
from django.template import Template, Context
from django.test.client import RequestFactory
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from topicblog.models import TopicBlogItem, TopicBlogLauncher, TopicBlogPanel
from datetime import datetime, timezone

from topicblog.templatetags.markdown import tn_markdown


class TBEmailTemplateTagsTests(TestCase):
    def test_email_full_width_image(self):
        # An existing static image
        filepath = "asso_tn/belvederes.jpg"
        alt_text = "Belvederes"
        link = "https://mobilitains.fr"
        template_string = (
            "{% load static %}{% load email_tags %}"
            "{% static "
            f"'{filepath}'"
            " as filepath %}"
            "{% email_full_width_image filepath "
            f"'{alt_text}' '{link}'"
            " %}"
        )
        context = Context()
        context["request"] = RequestFactory().get("/")
        rendered_template = Template(template_string).render(context)

        self.assertIn("belvederes.jpg", rendered_template)

    def test_email_body_text_md(self):
        text = "This is a test"
        expected_template = f"""
            <tr>
                <td style="padding:30px;background-color:#ffffff;">
                    <p style="margin:0;">
                        {tn_markdown({}, text)}
                    </p>
                </td>
            </tr>
            """
        template_string = (
            "{% load email_tags %}" "{% email_body_text_md text %}"
        )
        context = Context({"text": text})
        rendered_template = Template(template_string).render(context)
        # Get rid of the whitespaces
        rendered_template = " ".join(rendered_template.split())
        expected_template = " ".join(expected_template.split())
        self.assertEqual(rendered_template, expected_template)

    def test_email_cta_button(self):
        slug = "index"
        label = "Go to the homepage"

        template_string = (
            "{% load email_tags %}" "{% email_cta_button slug label %}"
        )

        def mock_get_host():
            return "127.0.0.1:8000"

        http_request = HttpRequest()
        http_request.get_host = mock_get_host
        context = Context(
            {"slug": slug, "label": label, "request": http_request}
        )
        rendered_template = Template(template_string).render(context)
        self.assertIn(label, rendered_template)
        self.assertIn(
            reverse("topic_blog:view_item_by_slug", args=[slug]),
            rendered_template,
        )


class TBLauncherTemplateTagsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="test-user", password="test-pass"
        )
        self.admin.save()
        self.item = TopicBlogItem.objects.create(
            slug="home",
            date_created=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.admin,
            template_name="topicblog/content.html",
            body_text_1_md="body 1",
            header_image="picture.png",
            title="Test-title",
        )
        self.item.save()
        self.launcher = TopicBlogLauncher.objects.create(
            slug="slug",
            launcher_image="picture.png",
            launcher_image_alt_text="picture",
            launcher_text_md="laucher text",
            teaser_chars=20,
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.admin,
            article_slug=self.item.slug,
            template_name="topicblog/content_launcher.html",
            headline="Headline",
        )
        self.launcher.save()

    def test_launcher(self):
        url = reverse_lazy(
            "topic_blog:view_item_by_slug", args=[self.launcher.article_slug]
        )
        link = f'<a href="{url}">'
        img = self.launcher.launcher_image.url
        alt = self.launcher.launcher_image_alt_text
        image = f'src="{img}" alt="{alt}"'
        title = f"{ self.launcher.headline }"
        text = f"{ self.launcher.launcher_text_md }"
        template_string = "{% load launcher %}" "{% launcher slug %}"
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
        url = reverse_lazy(
            "topic_blog:view_item_by_slug", args=[self.item.slug]
        )
        link = f'<a href="{url}"'
        title = (
            f'<h2 class="card-title text-white">{self.item.header_title}</h2>'
        )
        item_description = self.item.header_description
        description = f'<p class="card-text text-white">{item_description}</p>'
        text = f'<div class="teaser-text"> <p>{ self.item.body_text_1_md}</p>'
        template_string = "{% load launcher %}" "{% item_teaser slug %}"
        context = Context({"slug": self.launcher.slug})
        rendered_template = Template(template_string).render(context)
        rendered_template = " ".join(rendered_template.split())
        self.assertIn(link, rendered_template)
        self.assertIn(title, rendered_template)
        self.assertIn(description, rendered_template)
        self.assertIn(text, rendered_template)


class TestTopicBlogPanel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="testuser",
        )
        self.panel = TopicBlogPanel.objects.create(
            title="Test Panel Title",
            slug="test-panel",
            body_text_1_md="**This is a test panel.**",
            user=self.user,
            template_name="topicblog/panel_did_you_know_tip_1.html",
        )

    def test_inclusion_tag(self):
        """
        Check that the TBPanel is rendered with markdown using inclusion tag.
        """
        template_string = """{% load panels %}{% panel "test-panel" %}"""
        context = Context()
        context["request"] = RequestFactory().get("/")
        rendered = Template(template_string=template_string).render(
            context=context
        )
        self.assertIn("Test Panel Title", rendered)
        self.assertIn("This is a test panel.", rendered)
        self.assertIn("<strong>This is a test panel.</strong>", rendered)

    def test_tn_markdown_syntax(self):
        """Check that the TBPanel is rendered with markdown using tn_markdown.

        This test isn't in test_tn_links.py because the use of panel requires
        some setup : All panels aren't rendered the same, as they use
        a property to set their template, that will in turn
        set their rendering.
        """
        template_string = """
            {% load markdown %}
            {% load panels %}
            {% tn_markdown "[[panel:]]((test-panel))" %}
            """
        context = Context({"panel_slug": self.panel.slug})
        rendered = Template(template_string=template_string).render(
            context=context
        )
        self.assertIn("Test Panel Title", rendered)
        self.assertIn("This is a test panel.", rendered)
        self.assertIn("<strong>This is a test panel.</strong>", rendered)


class SocialTests(TestCase):
    def setUp(self) -> None:
        self.admin = User.objects.create_superuser(
            username="test-user", password="test-pass"
        )
        self.item = TopicBlogItem.objects.create(
            slug="home",
            date_created=datetime.now(timezone.utc),
            publication_date=datetime.now(timezone.utc),
            first_publication_date=datetime.now(timezone.utc),
            user=self.admin,
            template_name="topicblog/content.html",
            body_text_1_md="body 1",
            header_image="picture.png",
            title="Test-title",
        )

    def test_social_tag_rendering(self):
        template_string = "{% load social %}" "{% socials_share_buttons %}"
        rendered_template = Template(template_string).render(Context({}))
        self.assertIn(
            "https://twitter.com/intent/tweet?url=", rendered_template
        )
        self.assertIn(
            "http://www.facebook.com/share.php?u=", rendered_template
        )

    def test_social_tag_rendering_with_url(self):
        url = reverse_lazy(
            self.item.viewbyslug_object_url, args=[self.item.slug]
        )
        response = self.client.get(url)
        absolute_url = self.client.get(url).wsgi_request.build_absolute_uri()

        self.assertIn(
            "https://twitter.com/intent/tweet?url=" + quote(absolute_url),
            response.content.decode("utf-8"),
        )
        self.assertIn(
            "http://www.facebook.com/share.php?u=" + quote(absolute_url),
            response.content.decode("utf-8"),
        )
