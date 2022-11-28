from django import template
from topicblog.models import TopicBlogPanel
import logging

register = template.Library()

logger = logging.getLogger("django")


@register.inclusion_tag('topicblog/template_tags/panel.html', takes_context=True)
def panel(context: dict, slug: str, is_preview=False):
    if is_preview and context:
        panel = context.get("page")
    else:
        panel = TopicBlogPanel.objects.filter(
            slug__iexact=slug).order_by("-publication_date").first()
    if panel is None:
        logger.error(f"panel failed to find slug: \"{slug}\".")
    return {'page': panel}
