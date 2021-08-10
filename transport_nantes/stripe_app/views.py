import datetime

from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

import stripe

from .models import TrackingProgression
from .forms import DonationForm, AmountForm
from transport_nantes.settings import (ROLE, STRIPE_PUBLISHABLE_KEY,
                                       STRIPE_SECRET_KEY)


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


def create_checkout_session(request: dict) -> dict:
    """
    Create new Checkout Session for the order

    Other optional params include:
    [billing_address_collection] - to display
    billing address details on the page
    [customer] - if you have an existing Stripe Customer ID
    [payment_intent_data] - capture the payment later
    [customer_email] - prefill the email input in the form
    For full details see
    https://stripe.com/docs/api/checkout/sessions/create

    ?session_id={CHECKOUT_SESSION_ID} means the redirect
    will have the session ID set as a query param
    """
    if request.method == "POST":
        # We're forced to give a full URL, even if the request is local
        # Stripe uses HTTPS on live but tolerate http for test purpose.
        if ROLE == "dev":
            domain_url = "http://" + str(request.get_host())
        else:
            domain_url = "https://" + str(request.get_host())
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            # request.POST["donation_type"] is given with JavaScript
            # it can take two values : payment and subscription.
            if request.POST["donation_type"] == 'payment':
                checkout_session = stripe.checkout.Session.create(
                    # Links need to be valid
                    # Cant't use bare /donation, will raise an error.
                    success_url=domain_url + "/donation/success/",
                    cancel_url=domain_url + "/donation/",
                    payment_method_types=['card'],
                    mode=request.POST["donation_type"],
                    customer_email=request.POST["mail"],
                    line_items=[
                        {
                            'name': 'Donation',
                            'quantity': 1,
                            'currency': 'eur',
                            # Amount in cents
                            'amount': order_amount(request.POST),
                        }
                    ],
                    # Metadata is an optional field containing all personal
                    # informations gathered in the form.
                    metadata=request.POST
                )
                return JsonResponse({'sessionId': checkout_session['id']})

            # There are fewer parameters for subscription because some of them
            # are set on Stripe's Dashboard.
            # Subscriptions are created in the dashboard only.
            elif request.POST["donation_type"] == "subscription":
                checkout_session = stripe.checkout.Session.create(
                    # Links need to be valid
                    success_url=domain_url + "/donation/success/",
                    cancel_url=domain_url + "/donation/",
                    payment_method_types=['card'],
                    mode=request.POST["donation_type"],
                    customer_email=request.POST["mail"],
                    line_items=[
                        {
                            'quantity': 1,
                            # product id from Stripe's Dashboard.
                            # Exemple : price_1J0of7ClnCBJWy551iIQ6ydg
                            # Hardcoded in get_subscription_amounts()
                            'price': request.POST["subscription_amount"],
                        }
                    ],
                    metadata=request.POST
                )
                return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as error_message:
            return JsonResponse({'error': str(error_message)})


def order_amount(items: dict) -> int:
    """
    Take the donation amount (in euros) in returns it in centimes.

    items: content of request.POST
    """

    # "0" indicates that user selected "Montant libre"
    if items["payment_amount"] == "0":
        # "Free amount" field is a string input by user in the form.
        # The form wont let non numeric values be entered.
        return int(items["free_amount"])*100
    else:
        return int(items["payment_amount"])*100


class SuccessView(TemplateView):
    """
    Only used to display a static template.
    This template is displayed if the Stripe payment is completed.
    """
    template_name = "stripe_app/success.html"


def tracking_progression(request: dict) -> TrackingProgression:
    """
    Creates a TrackingProgression instance and saves it into DB
    request contains 2 bool representing each step of donation form.
    bool are in JS format 'true'/'false' and not read by Python as bool
    and as a consequence it needs to be transformed into Python bool.
    """
    try:
        data = request.POST
        data = data.dict()
        for key, _ in data.items():
            if data[key] == "true":
                data[key] = True
            else:
                data[key] = False

        data = TrackingProgression(amount_form_done=data["step_1_completed"],
                                   donation_form_done=data["step_2_completed"],
                                   timestamp=datetime.datetime.now)
        data.save()
        return HttpResponse(status=200)
    except Exception as error_message:
        print("error message: ", error_message)
        return JsonResponse({'error': str(error_message)})
