from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import JsonResponse

from .forms import DonationForm, AmountForm

from transport_nantes.settings import (ROLE, STRIPE_PUBLISHABLE_KEY)


class StripeView(TemplateView):
    """
    Displays the two forms required to make the donation page.
    """
    template_name = "stripe_app/donation_form.html"
    form_class = DonationForm

    def get(self, request, *args, **kwargs):
        """
        Main function used, will pass the appropriate form to the template.
        """
        info_form = DonationForm()
        amount_form = AmountForm()
        amount_form.fields["payment_amount"].choices = get_amount_choices()
        amount_form.fields["subscription_amount"].choices = get_subscription_amounts() # noqa
        return render(request, self.template_name, {"info_form": info_form,
                                                    "amount_form": amount_form
                                                    })


def get_subscription_amounts():
    """Get the Stripe key and description string of subscription options.

    For the moment, this is hard-coded here.  The intent is that these
    values will be provided by the database combined, perhaps, with
    some algorithmic hints on the donation levels to encourage.

    The first value of each tuple is a key provided by Stripe.  These
    values correspond to registered products which we must create
    manually (perhaps eventually via API) on their web dashboard.

    The second value of each tuple is a French string to display to
    the user to indicate the value of the corresponding subscription
    choice.

    """
    if ROLE == 'production':
        subscription_choices = [("price_1JKfNuClnCBJWy55SxZWROd3", "5 euros"),
                                ("price_1IIGzvClnCBJWy55MCIEkMpE", "10 euros"),
                                ("price_1JKfOBClnCBJWy55LX4ctrrc", "15 euros"),
                                ("price_1JKfOVClnCBJWy55HGa9OXcz", "20 euros")]
    else:
        subscription_choices = [("price_1J0of7ClnCBJWy551iIQ6ydg", "8 euros"),
                                ("price_1J0ogXClnCBJWy552i9Bs2bg", "12 euros"),
                                ("price_1J0ohVClnCBJWy55dAJxHjXE", "20 euros"),
                                ("price_1JKgKtClnCBJWy55Ob7PeJs8", "30 euros")]
    return subscription_choices


def get_amount_choices():
    """Provide the set of choices to display to users for one-off gifts.

    For the moment, this is hard-coded here.  The intent is that these
    values will be provided by the database combined, perhaps, with
    some algorithmic hints on the donation levels to encourage.

    The first value of each tuple is the amount.  The second is a
    French string to display to the user to indicate the value of the
    choice.

    """

    amount_choices = [(5, "5 euros"),
                      (10, "10 euros"),
                      (25, "25 euros"),
                      (0, "Montant libre")]
    return amount_choices


def get_public_key(request):
    """
    Returns the public key of the stripe account.
    """
    if request.method == "GET":
        public_key = {"publicKey": STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(public_key, safe=False)
