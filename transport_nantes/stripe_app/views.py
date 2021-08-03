import json
import datetime

from django.views.generic.base import TemplateView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import stripe

from transport_nantes.settings import (
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET)
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
        return render(request, self.template_name, {"info_form": info_form,
                                                    "amount_form": amount_form
                                                    })

    def post(self, request, *args, **kwargs):
        """
        Used for debug, not used in production.
        The forms aren't POSTed using POST on this URL.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            print(form.cleaned_data)
            print(type(form.cleaned_data))

        return render(request, self.template_name, {'form': form})


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
            # DEBUG
            print(f'{request.POST}')
            print("donation type is: ", request.POST["donation_type"])

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
                print(checkout_session)
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
                            # Amount in cents
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
        # TODO: run some custom code here
        print("Details attached to event : \n\n", "="*30, "\n", event)
        try:
            pass
            # make_donor_from_webhook(event)
            # make_donation_from_webhook(event)
        except Exception as error_message:
            print("="*80, "\n", "Error while creating \
            a new Donor or Donation. Details : ", error_message)

    return HttpResponse(status=200)


# def make_donor_from_webhook(event):
#     """
#     Creates a new donor entry in the database from
#     informations in the event.
#     event is sent by Stripe in the validaiton process of
#     the payment.
#     Metadata originates from the form on donation page,
#     and is sent using JavaScript to Stripe.
#     """
#     kwargs = {
#         "email": event["data"]["object"]["customer_email"],
#         "first_name": event["data"]["object"]["metadata"]["first_name"],
#         "last_name": event["data"]["object"]["metadata"]["last_name"],
#         "telephone": event["data"]["object"]["metadata"]["telephone"],
#         "title": event["data"]["object"]["metadata"]["title"],
#         "address": event["data"]["object"]["metadata"]["address"],
#         "more_adress": event["data"]["object"]["metadata"]["more_adress"],
#         "postal_code": event["data"]["object"]["metadata"]["postal_code"],
#         "city": event["data"]["object"]["metadata"]["city"],
#         "country": event["data"]["object"]["metadata"]["country"],
#     }
#     donor = Donor(**kwargs)
#     donor.save()
#     print("Donor created !")


# def make_donation_from_webhook(event):
#     """
#     Creates an entry in database from informations in the event.
#     event is sent by Stripe in the validation process of donation.
#     """
#     if event["data"]["object"]["mode"] == "subscription":
#         mode = "SUB"
#     else:
#         mode = "PAY"

#     kwargs = {
#         "donor": Donor.objects.get(
#             email=event["data"]["object"]["customer_email"]),
#         "mode": mode,
#         "amount": int(event["data"]["object"]["amount_total"])
#     }

#     donation = Donation(**kwargs)
#     donation.save()
#     print("Donation created !")


def order_amount(items):
    # Here the formula to compute order amount.
    # We aim for one time donations and recurring donations.
    # Order amount will depend on the form we will implement later on.
    # Amount is in cents. 1000 = 10¤
    # Computing the amount server side prevents user from manipulating datas.
    # Items should only contain a list of item that iterate through
    # to get a proper price.

    # Either equal to "payment" or "subscription"
    donation_type = items["donation_type"]

    # "0" indicates that user selected "Montant libre"
    if items[donation_type + "_amount"] == "0":
        return int(items["free_amount"])*100
    else:
        return int(items[donation_type + "_amount"])*100


def create_payment_intent(request):
    try:
        # request.body will be a dict containing items,
        # retrieved in the browser's JS.
        data = json.loads(request.body)
        intent = stripe.PaymentIntent.create(
            amount=order_amount(data['items']),
            currency="eur",
            api_key=STRIPE_SECRET_KEY
        )
        print("client secret :", intent["client_secret"])
        return JsonResponse({'clientSecret': intent['client_secret']})

    except Exception as error_message:
        return JsonResponse({'error': str(error_message)})


def tracking_progression(request):
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
