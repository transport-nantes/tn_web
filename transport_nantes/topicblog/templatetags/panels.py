from django import template
from topicblog.models import TopicBlogPanel
import logging
from topicblog.views import k_render_as_email

register = template.Library()

logger = logging.getLogger("django")


@register.inclusion_tag(
    "topicblog/template_tags/panel.html", takes_context=True
)
def panel(context: dict, slug: str, is_preview=False):
    """Render a panel tag.

    This is a hideous hack, passing arguments differently depending on
    context (preview, which means unpublished TB entries, or not
    preview).  That's something that's a bit pervasive in TopicBlog
    and that deserves a refactor one of these days.

    In the mean time, expect the slug to arrive as a string.

    """
    if is_preview and context:
        panel = context.get("page")
    else:
        panel = (
            TopicBlogPanel.objects.filter(slug__iexact=slug)
            .order_by("-publication_date")
            .first()
        )
    if panel is None:
        logger.error(f'panel failed to find slug: "{slug}".')
    return {
        "page": panel,
        "render_as_email": k_render_as_email in context,
    }
