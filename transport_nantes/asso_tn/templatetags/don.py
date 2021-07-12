from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# hello_asso_2019 = """https://www.helloasso.com/associations/transport-nantes/adhesions/adhesion-transport-nantes-2019/"""
hello_asso_join = """https://www.helloasso.com/associations/transport-nantes/adhesions/adhesion-transport-nantes-2019/"""
hello_asso_don = """https://www.helloasso.com/associations/transport-nantes/formulaires/2"""

@register.simple_tag
def bouton_don(link_text):
    return mark_safe(
        """<a href="{url}" class="btn btn-primary" role="button" target="_blank">{text}</a>""".format(
            url=hello_asso_don,
            text=link_text)
    )

@register.simple_tag
def bouton_join(link_text):
    return mark_safe(
        """<a href="{url}" class="btn donation-button btn-sm" role="button" target="_blank">{text}</a>""".format(
            url=hello_asso_join,
            text=link_text)
    )

@register.simple_tag
def bouton_don_lg(link_text):
    html_template = """<p class="pl-5"><a href="{link_url}" class="btn """ + \
        """donation-button btn-lg" target="_blank">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(link_url=hello_asso_don, text=link_text))

@register.simple_tag
def lien_don(link_text):
    return mark_safe(
        """<a href="{url}" target="_blank">{text}</a></p>""".format(
            url=hello_asso_don,
            text=link_text)
    )

@register.simple_tag
def url_don():
    return mark_safe(hello_asso_don)

@register.simple_tag
def external_url(url, label):
    html = """<a href="{url}" target="_blank">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)

@register.simple_tag
def external_url_button(url, label):
    html = """<p class="pl-5"> """ + \
	"""<a href="{url}" target="_blank" """ + \
	"""class="btn btn-outline-primary btn-lg">{label} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html.format(url=url, label=label))

@register.simple_tag
def action_button(link_url, topic_name):
    html_template = """<p><a href="{link_url}" class="btn """ + \
        """cta-button btn-lg">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(link_url=link_url, text=topic_name))

@register.simple_tag
def contact_button(button_text, email_subject):
    """This might (should) someday become a form."""
    html_template = """<p class="pl-5"> """ + \
	"""<a href="mailto:jevousaide@transport-nantes.com?subject={subj}&nbsp;!" """ + \
	"""class="btn cta-button btn-lg">{text} """ + \
        """<i class="fa fa-arrow-right" area-hidden="true"></i></a></p>"""
    return mark_safe(html_template.format(subj=email_subject, text=button_text))
