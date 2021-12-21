from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse

register = template.Library()

page_donation = reverse("stripe_app:stripe")

@register.simple_tag
def bouton_don(link_text):
    return mark_safe(
        """<a href="{url}" class="btn donation-button" role="button" target="_blank"">{text}</a>""".format(
            url=page_donation,
            text=link_text)
    )

@register.simple_tag
def bouton_join(link_text):
    return mark_safe(
        """<a href="{url}" class="btn donation-button btn-sm" role="button" target="_blank">{text}</a>""".format(
            url=page_donation,
            text=link_text)
    )

@register.simple_tag
def bouton_don_lg(link_text):
    html_template = """<p class="pl-5"><a href="{link_url}" class="btn """ + \
        """donation-button btn-lg" target="_blank">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(link_url=page_donation, text=link_text))

@register.simple_tag
def lien_don(link_text):
    return mark_safe(
        """<a href="{url}" target="_blank">{text}</a></p>""".format(
            url=page_donation,
            text=link_text)
    )

@register.simple_tag
def url_don():
    return mark_safe(page_donation)

@register.simple_tag
def external_url(url, label):
    html = """<a href="{url}" target="_blank">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)

@register.simple_tag
def external_url_button(url, label):
    html = """<p class="pl-5"> """ + \
	"""<a href="{url}" target="_blank" """ + \
	"""class="btn navigation-button">{label} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html.format(url=url, label=label))

@register.simple_tag
def action_button(link_url, topic_name):
    html_template = """<p><a href="{link_url}" class="btn """ + \
        """donation-button btn-lg">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(link_url=link_url, text=topic_name))

@register.simple_tag
def contact_button(button_text, email_subject):
    """This might (should) someday become a form."""
    html_template = """<p class="pl-5"> """ + \
	"""<a href="mailto:jevousaide@transport-nantes.com?subject={subj}&nbsp;!" """ + \
	"""class="btn donation-button btn-lg">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(subj=email_subject, text=button_text))


@register.simple_tag
def full_width_fixed_amount_donation_button(message=None, amount=1, cta_message="Soutenir"):
    """Creates a banner with a message"""
    if message is None:
        message = "Soutenez les Mobilitains pour une meilleure mobilité." +\
            " Faites un don !"
    html_template = """<div id="donation-banner" class="d-flex flex-column justify-content-center background-ad-hoc-blue mb-3">""" + \
        """<div class="d-flex flex-column justify-content-center m-auto p-2">""" + \
        f"""<p>{message}</p>""" + \
        f"""{fixed_amount_donation_button(amount, cta_message)}""" + \
        """</div>""" + \
        """</div>"""  # noqa
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
    html_template = """<a href="{url}" class="btn donation-button">""" + \
        f"""{cta_message}</a>"""
    return mark_safe(html_template.format(
        url=reverse("stripe_app:quick_donation", args=[amount])
        )
    )
