from django import template
from mailing_list.forms import QuickMailingListSignupForm

register = template.Library()

@register.inclusion_tag('mailing_list/panel/mailing_list.html')
def show_mailing_list():
    """Offer to join the mailing list.

    """
    form = QuickMailingListSignupForm
    return {'form': form}
