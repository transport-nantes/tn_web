import datetime
import string
import random

from django.views.generic.base import TemplateView
from django.http.response import HttpResponseServerError
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.models import User

import stripe

from transport_nantes.settings import (
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET, ROLE)
from .forms import DonationForm, AmountForm
from .models import TrackingProgression, Donation


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


class SuccessView(TemplateView):
    """
    Only used to display a static template.
    This template is displayed if the Stripe payment is completed.
    """
    template_name = "stripe_app/success.html"


def get_public_key(request):
    """
    Returns the public key of the stripe account.
    """
    if request.method == "GET":
        public_key = {"publicKey": STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(public_key, safe=False)


def create_checkout_session(request):
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
        domain_url = "http://" + str(request.get_host())
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
                            # Hardcoded in forms.py
                            'price': request.POST["subscription_amount"],
                        }
                    ],
                    metadata=request.POST
                )
                return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as error_message:
            return JsonResponse({'error': str(error_message)})


# Can't let CSRF otherwise POST from Stripe are denied.
# See https://stripe.com/docs/webhooks/best-practices#csrf-protection
# Protection is done by signature verification, no one without the
# endpoint secret key can trigger an entry creation.
@csrf_exempt
def stripe_webhook(request):
    """
    The webhook is triggered when a payment attempt is done.
    POST request from Stripe contain a signature to authenticate the request.
    The signature is generated with the secret key of the stripe account.
    """
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    try:
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    except KeyError:
        return HttpResponse(status=400)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        # Invalid payload
        print("==== Payload ====")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        print("==== Signature ====")
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        print("Details attached to event : \n\n", "="*30, "\n", event)
        try:
            make_donation_from_webhook(event)
        except Exception as error_message:
            print("="*80, "\n", "Error while creating \
            a new Donation. Details : ", error_message)

    return HttpResponse(status=200)


def get_random_string(length=20) -> str:
    """
    Returns a random string of length "length"
    This random string will be used as username value to
    create a new user in get_user(email) function.
    """
    random_string = ''.join(random.choice(string.ascii_letters +
                                          string.digits) for _ in range(length)) # noqa
    print("Random string is : {}".format(random_string))
    return random_string


def get_user(email: str) -> User:
    """
    Use email adress to lookup if a user exists.

    If user doesn't exist, create one with a random username.

    Returns an instance of User class.
    """

    existing_users = User.objects.filter(email=email)

    if len(existing_users) > 1:
        return HttpResponseServerError("Too many users with that email.")

    if len(existing_users) == 1:
        print("user already exists")
        return existing_users[0]

    else:
        user = User()
        user.email = email
        user.username = get_random_string()
        user.is_active = False
        user.save()
        print("User created !")
        return user


def make_donation_from_webhook(event: dict) -> None:
    """
    Creates a new donation entry in the database from
    informations in the event.
    event is sent by Stripe in the validaiton process of
    the payment.
    Metadata originates from the form on donation page,
    and is sent using JavaScript to Stripe.
    """
    # Determine if the user did a single time donation or a subcription.
    if event["data"]["object"]["mode"] == "subscription":
        # Subscription
        mode = "1"
    else:
        # Payment
        mode = "0"

    # kwargs to be used to create a Donation object.
    kwargs = {
        "user": get_user(event["data"]["object"]["customer_email"]),
        "email": event["data"]["object"]["customer_email"],
        "first_name": event["data"]["object"]["metadata"]["first_name"],
        "last_name": event["data"]["object"]["metadata"]["last_name"],
        "address": event["data"]["object"]["metadata"]["address"],
        "more_address": event["data"]["object"]["metadata"]["more_adress"],
        "postal_code": event["data"]["object"]["metadata"]["postal_code"],
        "city": event["data"]["object"]["metadata"]["city"],
        "country": event["data"]["object"]["metadata"]["country"],
        "periodicity_months": mode,
        "amount_centimes_euros": int(event["data"]["object"]["amount_total"]),
    }
    print("Creation of donation...")
    donation = Donation(**kwargs)
    donation.save()
    print("Donation entry created !")


def order_amount(items: dict) -> int:
    """
    Take the donation amount (in euros) in returns it in centimes.

    items: content of request.POST
    """

    # Either equal to "payment" or "subscription"
    donation_type = items["donation_type"]

    # "0" indicates that user selected "Montant libre"
    if items[donation_type + "_amount"] == "0":
        # "Free amount" field is a string input by user in the form.
        # The form wont let non numeric values be entered.
        return int(items["free_amount"])*100
    else:
        return int(items[donation_type + "_amount"])*100


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
