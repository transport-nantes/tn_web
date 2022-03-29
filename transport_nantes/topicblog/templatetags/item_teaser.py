from django import template
from topicblog.models import TopicBlogItem
import logging

register = template.Library()

logger = logging.getLogger("django")


@register.inclusion_tag('topicblog/template_tags/item_teaser.html')
def item_teaser(slug, truncate_after=50):
    item = TopicBlogItem.objects.filter(
        slug__iexact=slug, publication_date__isnull=False).first()
    if item is None:
        logger.error(f"item_teaser failed to find slug: \"{slug}\".")
    return {'item': item, 'truncate_after': truncate_after}
