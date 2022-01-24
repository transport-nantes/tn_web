from django import template
from django.templatetags.static import static

register = template.Library()


def get_image_url(image):
    """Return the url of the image

    """
    if image is None:
        return None
    elif isinstance(image, str):
        return static(image)
    return image.url


@register.simple_tag
def first_not_empty(*args):
    """Return the first not empty argument

    """
    for arg in args:
        if arg:
            return arg
    return None


@register.simple_tag
def first_not_empty_image(*args):
    """Return the url of the first not empty image

    """
    image = first_not_empty(*args)
    return get_image_url(image)
