from django import template
from topicblog.models import TopicBlogLauncher
register = template.Library()


@register.inclusion_tag('topicblog/template_tags/launcher.html')
def launcher(slug):
    launcher = TopicBlogLauncher.objects.filter(
        slug__iexact=slug, publication_date__isnull=False).first()
    return {'launcher': launcher}
