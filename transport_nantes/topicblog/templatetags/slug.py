from django import template
from django.utils.html import mark_safe
from django.urls import reverse

from topicblog.views import k_render_as_email

register = template.Library()


@register.simple_tag(takes_context=True)
def tbi_slug(context: dict, label: str, slug: str):
    """Render an internal TBItem link from a slug.

    The value must include everything after "/tb/t/".

    Usage:

      {% tbi_slug "my-slug" %}
    """
    url = reverse('topic_blog:view_item_by_slug', args=[slug])
    if k_render_as_email in context:
        # Rendering to email, so need absolute URL.
        request = context['request']
        url = request.build_absolute_uri(url)
    html = """<a href="{url}">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)
