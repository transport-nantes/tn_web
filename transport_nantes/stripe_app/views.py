from django.views.generic.base import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import stripe

from transport_nantes.settings import STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY


class StripeView(TemplateView):
    template_name = "stripe_app/test.html"

@csrf_exempt
def get_public_key(request):
    if request.method == "GET":
        public_key = {"publicKey": STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(public_key, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == "GET":
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
            checkout_session = stripe.checkout.Session.create(
                # Links need to be valid
                success_url= domain_url + "/checkout/success/",
                cancel_url= domain_url+ "/checkout/cancelled/",
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'name': 'Donation',
                        'quantity': 1,
                        'currency': 'eur',
                        # Amount in cents
                        'amount': '1000',
                    }
                ]
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})
