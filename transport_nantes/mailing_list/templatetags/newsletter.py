from django import template
from mailing_list.forms import QuickMailingListSignupForm
from mailing_list.forms import QuickPetitionSignupForm

register = template.Library()

@register.inclusion_tag('mailing_list/panel/mailing_list.html')
def show_mailing_list():
    """Offer to join the mailing list.

    """
    form = QuickMailingListSignupForm
    return {'form': form}

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
