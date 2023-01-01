from django.utils.crypto import get_random_string
from django import template
from django.template import Node

register = template.Library()


class RandomNode(Node):
    def render(self, context):
        context["randomstring"] = get_random_string()
        return ""


@register.tag
def randomstring(parser, token):
    """
    Emit a random string.
    """
    return RandomNode()
