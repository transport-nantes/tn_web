from django import template
from topicblog.models import TopicBlogLauncher, TopicBlogItem
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


@register.inclusion_tag('topicblog/template_tags/item_teaser.html')
def item_teaser(slug):
    launcher = TopicBlogLauncher.objects.filter(
        slug__iexact=slug, publication_date__isnull=False).first()
    if launcher is None:
        logger.error(f"item_teaser failed to find slug: \"{slug}\".")
        item = None
    else:
        item = TopicBlogItem.objects.filter(
            slug__iexact=launcher.article_slug, publication_date__isnull=False).first()
        if item is None:
            logger.error(f"item_teaser failed to find slug: \"{slug}\".")
    return {'launcher': launcher, 'item': item}
