import json

from django.views.generic.base import TemplateView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import stripe

from transport_nantes.settings import (
    STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET)
from .forms import DonationForm, AmountForm


class StripeView(TemplateView):
    template_name = "stripe_app/donation_form.html"
    form_class = DonationForm

    def get(self, request, *args, **kwargs):
        info_form = DonationForm()
        amount_form = AmountForm()
        return render(request, self.template_name, {"info_form": info_form,
                                                    "amount_form": amount_form
                                                    })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # <process form cleaned data>
            print(form.cleaned_data)
            print(type(form.cleaned_data))

        return render(request, self.template_name, {'form': form})

class SuccessView(TemplateView):
    template_name = "stripe_app/success.html"

@csrf_exempt
def get_public_key(request):
    if request.method == "GET":
        public_key = {"publicKey": STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(public_key, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        domain_url = "http://" + str(request.get_host())
        stripe.api_key = STRIPE_SECRET_KEY
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display
            # billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see
            # https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect
            # will have the session ID set as a query param
            print(f'{request.POST}')
            form = DonationForm(request.POST)
            if form.is_valid():
                checkout_session = stripe.checkout.Session.create(
                    # Links need to be valid
                    success_url= domain_url + "/donation/success/",
                    cancel_url= domain_url+ "/donation/",
                    payment_method_types=['card'],
                    mode='payment',
                    customer_email= request.POST["mail"],
                    line_items=[
                        {
                            'name': 'Donation',
                            'quantity': 1,
                            'currency': 'eur',
                            # Amount in cents
                            'amount': order_amount(request.POST),
                        }
                    ]
                )
                return JsonResponse({'sessionId': checkout_session['id']})
            else:
                return render(
                    request, "stripe_app/donation_form.html", {'form': form})
        except Exception as error_message:
            return JsonResponse({'error': str(error_message)})

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
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

    return HttpResponse(status=200)

@csrf_exempt
def order_amount(items):
    # Here the formula to compute order amount.
    # We aim for one time donations and recurring donations.
    # Order amount will depend on the form we will implement later on.
    # Amount is in cents. 1000 = 10¤
    # Computing the amount server side prevents user from manipulating datas.
    # Items should only contain a list of item that iterate through
    # to get a proper price.
    if items["free_amount"] != "" and items['amount'] == "0":
        return int(items["free_amount"])*100
    else:
        return int(items["amount"])*100


@csrf_exempt
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

def form_validation(request):
    form = DonationForm(request.POST)
    print(f"{form=}")
    if form.is_valid():
        print("form is valid")
        return JsonResponse({"validity": True})
    else:
        print("form is invalid")
        return JsonResponse({"validity": False})
