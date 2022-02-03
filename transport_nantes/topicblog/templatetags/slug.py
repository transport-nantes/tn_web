from django import template
from django.utils.html import mark_safe
from django.urls import reverse

register = template.Library()


@register.simple_tag
def tbi_slug(slug, label):
    """Render an internal TBItem link from a slug.

    The value must include everything after "/tb/t/".

    Usage:

      {% tbi_slug "my-slug" %}
    """
    url = reverse('topic_blog:view_item_by_slug', args=[slug])
    html = """<a href="{url}">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)
