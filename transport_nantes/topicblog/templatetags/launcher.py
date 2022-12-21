from django import template
from topicblog.models import TopicBlogLauncher, TopicBlogItem
import logging

register = template.Library()

logger = logging.getLogger("django")


@register.inclusion_tag('topicblog/template_tags/launcher.html',
                        takes_context=True)
def launcher(context, slug, is_preview=False):
    if is_preview:
        # In TBBaseViewOne, "page" holds the object we're trying to visualize.
        # ViewOne is a view made to display a single object.
        launcher = context["page"]
    else:
        # In the context of a launcher displayed in another view than ViewOne,
        # we need to get the object from the database, as the "page" variable
        # is not available. (typically in the index)
        # because no database rule enforces the rule "one publication date per
        # slug", we need to get the most recent one just in case
        launcher = TopicBlogLauncher.objects.filter(
            slug__iexact=slug, publication_date__isnull=False
            ).order_by("-publication_date").first()
    if launcher is None:
        logger.error(f"item_teaser failed to find slug: \"{slug}\".")
    return {'launcher': launcher}


@register.inclusion_tag('topicblog/template_tags/launcher_carousel.html',
                        takes_context=True)
def launcher_carousel(context, slug, is_preview=False):
    """Launcher, but with a different template to render inside a carousel."""
    return launcher(context, slug, is_preview)


@register.inclusion_tag('topicblog/template_tags/item_teaser.html',
                        takes_context=True)
def item_teaser(context, slug, is_preview=False):
    if is_preview:
        # In TBBaseViewOne, "page" holds the object we're trying to visualize.
        # ViewOne is a view made to display a single object.
        launcher = context["page"]
    else:
        # In the context of a launcher displayed in another view than ViewOne,
        # we need to get the object from the database, as the "page" variable
        # is not available. (typically in the index)
        # because no database rule enforces the rule "one publication date per
        # slug", we need to get the most recent one just in case
        launcher = TopicBlogLauncher.objects.filter(
            slug__iexact=slug, publication_date__isnull=False
            ).order_by("-publication_date").first()

    if launcher is None:
        logger.error(f"item_teaser failed to find slug: \"{slug}\".")
        item = None
    else:
        # because no database rule enforces the rule "one publication date per
        # slug", we need to get the most recent one just in case
        item = TopicBlogItem.objects.filter(
            slug__iexact=launcher.article_slug, publication_date__isnull=False
            ).order_by("-publication_date").first()
        if item is None:
            logger.error(f"item_teaser failed to find slug: \"{slug}\".")
    return {'launcher': launcher, 'item': item}


@register.inclusion_tag('topicblog/template_tags/item_teaser_index.html',
                        takes_context=True)
def item_teaser_index(context, slug, is_preview=False):
    """Item teaser, but with a different template to render in the index."""
    return item_teaser(context, slug, is_preview)
