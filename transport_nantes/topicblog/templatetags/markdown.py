from django import template
from django.utils.html import escape, mark_safe
from markdown2 import markdown

from topicblog.tn_links import TNLinkParser

register = template.Library()


@register.simple_tag(takes_context=True, name="tn_markdown")
def tn_markdown(context, value):
    """Safely render markdown to html.

    First escape any html so that we are sure the string is safe, then
    render to html so that a template may use the data as safe.

    Usage:

      {% tn_markdown md_text_variable %}
    """
    parser = TNLinkParser(context, verbose=False)
    return mark_safe(markdown(parser.transform(escape(value))))
