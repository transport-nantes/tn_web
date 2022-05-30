from django import template
from django.utils.html import mark_safe
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def tbi_slug(context, label, slug):
    """Render an internal TBItem link from a slug.

    The value must include everything after "/tb/t/".

    Usage:

      {% tbi_slug "my-slug" %}
    """
    if context.get('is_email'):
        request = context['request']
        url = request.build_absolute_uri(
          reverse('topic_blog:view_item_by_slug', args=[slug]))
    else:
        url = reverse('topic_blog:view_item_by_slug', args=[slug])

    html = """<a href="{url}">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)
