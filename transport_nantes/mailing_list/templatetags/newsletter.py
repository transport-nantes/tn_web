from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from mailing_list.forms import QuickMailingListSignupForm
from mailing_list.forms import QuickPetitionSignupForm

register = template.Library()

@register.inclusion_tag('mailing_list/panel/mailing_list.html', takes_context=True)
def show_mailing_list(context, **kwargs):
    """Offer to join the mailing list.

    The caller must provide a mailinglist name.  This makes no sense
    without, and we will 500 (our fault) without.

    Optionally provide a title.

    """
    if 'title' in kwargs:
        context['title'] = kwargs.get('title', "")
    mailinglist = kwargs.get('mailinglist')
    if mailinglist is None:
        mailinglist = context.get('mailinglist')
    form = QuickMailingListSignupForm(
        initial={"mailinglist": mailinglist})
    context['form'] = form
    return context

@register.inclusion_tag('mailing_list/panel/petition.html')
def show_petition_signup(petition_name):
    """Offer to sign a petition.

    This is almost the same as offering to sign one mailing list.  We
    make them separate functions because we fully expect them to
    diverge.  Initially, for example, signing a petition requests a
    name whereas a mailing list does not.

    """
    form = QuickPetitionSignupForm(
        initial={'petition_name': petition_name})
    return {'form': form}

@register.simple_tag
def petition_link(petition, label):
    try:
        url = reverse('mailing_list:petition', args=[petition])
    except NoReverseMatch:
        url = '(((pétition pas trouvé : {ps})))'.format(ps=petition)
    html = """<a href="{url}">{label}</a>""".format(
        url=url, label=label)
    return mark_safe(html)
