from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse, reverse_lazy

from topicblog.views import k_render_as_email

register = template.Library()

page_donation = reverse_lazy("stripe_app:stripe")

# Because emails don't handle classes in most cases,
# we hardcode the styles here instead of using a CSS file.
class_btn_navigation_button = (
    """display: inline-block; font-weight: 400; """
    """color: #212529; text-align: center; vertical-align: middle;"""
    """padding: .375rem .75rem; font-size: 1rem; line-height: 1.5;"""
    """border-radius: .25rem; background-color:  #43526e; """
    """border: 1px solid  #43526e; color: white; font-weight: 600;"""
    """text-decoration: none; """
)

class_btn_donation_button = (
    """display: inline-block; font-weight: 400; """
    """color: #212529; text-align: center; vertical-align: middle;"""
    """padding: .375rem .75rem; font-size: 1rem; line-height: 1.5;"""
    """border-radius: .25rem; background-color:  #5BC2E7; """
    """border: 1px solid  #5BC2E7; color: white; font-weight: 600;"""
    """text-decoration: none; """
)

class_btn_lg = (
    """padding: .5rem 1rem;font-size: 1.25rem;line-height: 1.5;"""
    """border-radius: .3rem;"""
)


@register.simple_tag
def bouton_don(link_text, context={}):

    if k_render_as_email in context:
        # Rendering to email, so need absolute URL.
        request = context["request"]
        absolute_url = request.build_absolute_uri(page_donation)
        html = (
            f"""<p><a href="{absolute_url}" role="button" target="_blank" """
            f"""style="{class_btn_donation_button}">{link_text}</a></p> """
        )
    else:
        html = (
            '<a href="{url}" class="btn donation-button"'
            'role="button" target="_blank"">{text}</a>'
        ).format(url=page_donation, text=link_text)
    return mark_safe(html)


@register.simple_tag
def bouton_join(link_text):
    return mark_safe(
        (
            '<a href="{url}" class="btn donation-button '
            'btn-sm" role="button" target="_blank">{text}</a>'
        ).format(url=page_donation, text=link_text)
    )


@register.simple_tag
def bouton_don_lg(link_text, context={}):

    if k_render_as_email in context:
        # Rendering to email, so need absolute URL.
        request = context["request"]
        absolute_url = request.build_absolute_uri(page_donation)
        html = (
            f"""<p><a href="{absolute_url}" """
            f""" style="{class_btn_donation_button} {class_btn_lg}" """
            f"""target="_blank">{link_text} &rarr;</a></p> """
        )
    else:
        html = (
            """<p><a href="{link_url}" class="btn """
            + """donation-button btn-lg" target="_blank">{text} """
            + """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
        )
        html = html.format(link_url=page_donation, text=link_text)
    return mark_safe(html)


@register.simple_tag
def lien_don(link_text):
    return mark_safe(
        """<a href="{url}" target="_blank">{text}</a></p>""".format(
            url=page_donation, text=link_text
        )
    )


@register.simple_tag
def url_don():
    return mark_safe(page_donation)


@register.simple_tag
def external_url(url, label):
    html = """<a href="{url}" target="_blank">{label}</a>""".format(
        url=url, label=label
    )
    return mark_safe(html)


@register.simple_tag
def external_url_button(url, label, context={}):

    if k_render_as_email in context:
        # Rendering to email, so need absolute URL.
        request = context["request"]
        url = request.build_absolute_uri(url)
        html = (
            """<p><a href="{url}" target="_blank" """
            f"""style="{class_btn_navigation_button}">"""
            """{label} &rarr;</a></p>"""
        )
    else:
        html = (
            """<p> """
            + """<a href="{url}" target="_blank" """
            + """class="btn navigation-button">{label} """
            + """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
        )

    return mark_safe(html.format(url=url, label=label))


@register.simple_tag
def action_button(link_url, topic_name, context={}):

    if k_render_as_email in context:
        # Rendering to email, so need absolute URL.
        request = context["request"]
        link_url = request.build_absolute_uri(link_url)
        html = (
            f"""<p><a href="{link_url}" """
            f""" style="{class_btn_donation_button} {class_btn_lg}" >"""
            f"""{topic_name} &rarr;</a></p> """
        )
    else:
        html = (
            """<p> """
            + """<a href="{link_url}" class="btn donation-button """
            + """btn-lg" target="_blank">{topic_name} """
            + """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
        )
        html = html.format(link_url=link_url, topic_name=topic_name)

    return mark_safe(html)


@register.simple_tag
def contact_button(button_text, email_subject):
    """This might (should) someday become a form."""
    html_template = (
        "<p>"
        '<a href="mailto:jevousaide@transport-nantes.com?subject={subj}&nbsp;!'
        'class="btn donation-button btn-lg">{text}'
        '<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>'
    )
    return mark_safe(
        html_template.format(subj=email_subject, text=button_text)
    )


@register.simple_tag
def full_width_fixed_amount_donation_button(
    message=None, amount=1, cta_message="Soutenir"
):
    """Creates a banner with a message"""
    if message is None:
        message = (
            "Soutenez les Mobilitains pour une meilleure mobilité."
            + " Faites un don !"
        )
    html_template = (
        """<div id="donation-banner" class="d-flex flex-column justify-content-center background-ad-hoc-blue mb-3">"""
        + """<div class="d-flex flex-column justify-content-center m-auto p-2">"""
        + f"""<p>{message}</p>"""
        + f"""{fixed_amount_donation_button(amount, cta_message)}"""
        + """</div>"""
        + """</div>"""
    )  # noqa
    return mark_safe(html_template)


@register.simple_tag
def fixed_amount_donation_button(amount=1, cta_message="Soutenir"):
    """Create a donation button with proposed fixed donation amount.

    Present a donation page with a fixed amount and optional
    additional donation.  We want to experiment with campaigns that
    present as simplified as possible a workflow, even if the donation
    received is less than we might otherwise hope.

    The amount is the fixed amount to display.
    The cta_message is the button text.

    """
    html_template = (
        """<a href="{url}" class="btn donation-button">"""
        + f"""{cta_message}</a>"""
    )
    return mark_safe(
        html_template.format(
            url=reverse("stripe_app:quick_donation", args=[amount])
        )
    )
