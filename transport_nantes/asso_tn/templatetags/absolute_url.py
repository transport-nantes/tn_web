from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def absolute_url(context, view_name, *args, **kwargs):
    request = context['request']
    return request.build_absolute_uri(
        reverse(view_name, args=args, kwargs=kwargs))


@register.simple_tag(takes_context=True)
def absolute_url_image(context, image_url):
    request = context['request']
    return request.build_absolute_uri(
        image_url)
