from django import template
from topicblog.models import TopicBlogLauncher
import logging

register = template.Library()

logger = logging.getLogger("django")

@register.inclusion_tag('topicblog/template_tags/launcher.html')
def launcher(slug):
    launcher = TopicBlogLauncher.objects.filter(
        slug__iexact=slug, publication_date__isnull=False).first()
    if launcher is None:
        logger.error(f"item_teaser failed to find slug: \"{slug}\".")
    return {'launcher': launcher}
