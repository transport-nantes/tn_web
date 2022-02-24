from django.conf import settings
from django.template import Template, Context
from django.test import TestCase
from django.urls import reverse_lazy


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
