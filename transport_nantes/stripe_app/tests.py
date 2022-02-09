from stripe.webhook import WebhookSignature
from datetime import datetime

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .views import stripe_webhook
from .models import Donation


class StripeAppTests(TestCase):

    def setUp(self):
        self.timestamp = int(datetime.now().timestamp())
        self.factory = RequestFactory()
        self.checkout_session_completed_sub_payload = \
            b'{\n  "id": "evt_1KReZuClnCBJWy55jnEhLQ9H",\n  "object": "event",\n  "api_version": "2020-08-27",\n  "created": 1644506942,\n  "data": {\n    "object": {\n      "id": "cs_test_a1P7GbDJbtfBG96HpRAf1AFvz0UMB3XWv1cBkndQxtSBMWQ5vzVlnlLu1R",\n      "object": "checkout.session",\n      "after_expiration": null,\n      "allow_promotion_codes": null,\n      "amount_subtotal": 3000,\n      "amount_total": 3000,\n      "automatic_tax": {\n        "enabled": false,\n        "status": null\n      },\n      "billing_address_collection": null,\n      "cancel_url": "http://127.0.0.1:8000/donation/",\n      "client_reference_id": null,\n      "consent": null,\n      "consent_collection": null,\n      "currency": "eur",\n      "customer": "cus_L7uOLpyHjoItiF",\n      "customer_creation": "always",\n      "customer_details": {\n        "email": "newsub2@domain.com",\n        "phone": null,\n        "tax_exempt": "none",\n        "tax_ids": [\n\n        ]\n      },\n      "customer_email": "newsub2@domain.com",\n      "expires_at": 1644593327,\n      "livemode": false,\n      "locale": null,\n      "metadata": {\n        "csrfmiddlewaretoken": "9I8xk7lAx0AGWyq2hARP9jllM4dUM60KkYOQAjKTwA9xzp1qTacLNLIeA9jKU3ZO",\n        "donation_type": "subscription",\n        "subscription_amount": "price_1JKgKtClnCBJWy55Ob7PeJs8",\n        "free_amount": "",\n        "mail": "newsub2@domain.com",\n        "first_name": "CustomUser",\n        "last_name": "Doe",\n        "address": "221B Baker street",\n        "more_adress": "",\n        "postal_code": "33200",\n        "city": "London",\n        "country": "FR",\n        "originating_view": "StripeView",\n        "originating_parameters": "null"\n      },\n      "mode": "subscription",\n      "payment_intent": null,\n      "payment_link": null,\n      "payment_method_options": {\n      },\n      "payment_method_types": [\n        "card"\n      ],\n      "payment_status": "paid",\n      "phone_number_collection": {\n        "enabled": false\n      },\n      "recovered_from": null,\n      "setup_intent": null,\n      "shipping": null,\n      "shipping_address_collection": null,\n      "shipping_options": [\n\n      ],\n      "shipping_rate": null,\n      "status": "complete",\n      "submit_type": null,\n      "subscription": "sub_1KReZrClnCBJWy556NyE96aD",\n      "success_url": "http://127.0.0.1:8000/donation/success/",\n      "total_details": {\n        "amount_discount": 0,\n        "amount_shipping": 0,\n        "amount_tax": 0\n      },\n      "url": null\n    }\n  },\n  "livemode": false,\n  "pending_webhooks": 3,\n  "request": {\n    "id": "req_kUo0f0axctsHsp",\n    "idempotency_key": "fe759a67-7042-4a78-9a84-f5e9f3833611"\n  },\n  "type": "checkout.session.completed"\n}'

    def _get_signature(self, payload):
        # # https://stripe.com/docs/webhooks/signatures#prepare-payload
        decoded_payload = \
            payload.decode('utf-8')
        signed_payload = f'{self.timestamp}.{decoded_payload}'
        expected_signature = WebhookSignature._compute_signature(
            signed_payload,
            settings.STRIPE_ENDPOINT_SECRET)

        return expected_signature

    def post_payload_to_webhook(self, payload):
        expected_signature = self._get_signature(
            payload)
        request = self.factory.post(
            reverse('stripe_app:webhook'),
            data=payload,
            content_type='application/json',
            HTTP_STRIPE_SIGNATURE=(f't={self.timestamp},'
                                   f'v1={expected_signature}'
                                   ',v0=placeholder')
            )
        response = stripe_webhook(request)
        return response

    def test_new_sub_registration(self):
        response = self.post_payload_to_webhook(
            self.checkout_session_completed_sub_payload)
        self.assertEqual(response.status_code, 200)

        number_of_donations = Donation.objects.count()
        self.assertEqual(number_of_donations, 1)
