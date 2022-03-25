from django import template
from topicblog.models import TopicBlogItem
register = template.Library()


@register.inclusion_tag('topicblog/template_tags/item_teaser.html')
def item_teaser(slug):
    item = TopicBlogItem.objects.filter(
        slug__iexact=slug, publication_date__isnull=False).first()
    return {'item': item}
