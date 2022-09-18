from django import template
import datetime
from django.utils.timezone import make_aware
from django.db.models import Count, Max
from utm.models import Visit

register = template.Library()

@register.inclusion_tag('utm/visit_overview.html', takes_context=True)
def visit_overview(context):
    """Provide a short summary of page visits.
    """
    time_now = make_aware(datetime.datetime.now())
    request = context['request']
    path = request.path
    robots = Visit.objects.filter(base_url=path, ua_is_bot=True)
    humans = Visit.objects.filter(base_url=path, ua_is_bot=False)
    humans_unique = Visit.objects.filter(base_url=path, ua_is_bot=False) \
                               .values('session_id').distinct()
    context['robots_48h'] = robots.filter(
        timestamp__gt=(time_now - datetime.timedelta(hours=48))).\
        count()
    context['humans_48h'] = humans.filter(
        timestamp__gt=(time_now - datetime.timedelta(hours=48))).\
        count()
    context['humans_unique_48h'] = humans_unique.filter(
        timestamp__gt=(time_now - datetime.timedelta(hours=48))).\
        count()

    context['robots_7j'] = robots.filter(
        timestamp__gt=(time_now - datetime.timedelta(days=7))).\
        count()
    context['humans_7j'] = humans.filter(
        timestamp__gt=(time_now - datetime.timedelta(days=7))).\
        count()
    context['humans_unique_7j'] = humans_unique.filter(
        timestamp__gt=(time_now - datetime.timedelta(days=7))).\
        count()

    context['robots'] = robots.count()
    context['humans'] = humans.count()
    context['humans_unique'] = humans_unique.count()

    sources = Visit.objects.filter(base_url=path, ua_is_bot=False) \
                         .values('source').distinct()
    context['sources'] = {}
    for source in sources:
        this_source = source['source']
        the_count = Visit.objects.filter(
            base_url=path, source=this_source, ua_is_bot=False) \
                               .values('session_id').distinct().count()
        if "" == this_source:
            # This should be doable with the |default filter in the template
            # but that's not working for me.
            this_source = "<aucun>"
        context['sources'][this_source] = the_count
    mediums = Visit.objects.filter(base_url=path, ua_is_bot=False) \
                         .values('medium').distinct()
    context['mediums'] = {}
    for medium in mediums:
        this_medium = medium['medium']
        the_count = Visit.objects.filter(
            base_url=path, medium=this_medium, ua_is_bot=False) \
                               .values('session_id').distinct().count()
        if "" == this_medium:
            # This should be doable with the |default filter in the template
            # but that's not working for me.
            this_medium = "<aucun>"
        context['mediums'][this_medium] = the_count
    return context
