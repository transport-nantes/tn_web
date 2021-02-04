from django import template
from django.utils.html import escape, mark_safe
from markdown2 import markdown

from topicblog.tn_links import TNLinkParser

register = template.Library()

@register.filter(name='markdown')
def safe_markdown(value):
    """Safely render markdown to html.

    First escape any html so that we are sure the string is safe.

    Then render markdown to html so that we can render
    in a template as safe.

    Usage:

      {{ value|markdown }}
    """
    parser = TNLinkParser(verbose=False)
    return mark_safe(markdown(parser.transform(escape(value))))
