from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.test import LiveServerTestCase, RequestFactory, TestCase
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from stripe.webhook import WebhookSignature
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from .models import Donation
from .views import stripe_webhook


class StripeAppTests(TestCase):
    def setUp(self):
        self.timestamp = int(datetime.now().timestamp())
        self.factory = RequestFactory()
        self.checkout_session_completed_sub_payload = b'{\n  "id": "evt_1KReZuClnCBJWy55jnEhLQ9H",\n  "object": "event",\n  "api_version": "2020-08-27",\n  "created": 1644506942,\n  "data": {\n    "object": {\n      "id": "cs_test_a1P7GbDJbtfBG96HpRAf1AFvz0UMB3XWv1cBkndQxtSBMWQ5vzVlnlLu1R",\n      "object": "checkout.session",\n      "after_expiration": null,\n      "allow_promotion_codes": null,\n      "amount_subtotal": 3000,\n      "amount_total": 3000,\n      "automatic_tax": {\n        "enabled": false,\n        "status": null\n      },\n      "billing_address_collection": null,\n      "cancel_url": "http://127.0.0.1:8000/donation/",\n      "client_reference_id": null,\n      "consent": null,\n      "consent_collection": null,\n      "currency": "eur",\n      "customer": "cus_L7uOLpyHjoItiF",\n      "customer_creation": "always",\n      "customer_details": {\n        "email": "newsub2@domain.com",\n        "phone": null,\n        "tax_exempt": "none",\n        "tax_ids": [\n\n        ]\n      },\n      "customer_email": "newsub2@domain.com",\n      "expires_at": 1644593327,\n      "livemode": false,\n      "locale": null,\n      "metadata": {\n        "csrfmiddlewaretoken": "9I8xk7lAx0AGWyq2hARP9jllM4dUM60KkYOQAjKTwA9xzp1qTacLNLIeA9jKU3ZO",\n        "donation_type": "subscription",\n        "subscription_amount": "price_1JKgKtClnCBJWy55Ob7PeJs8",\n        "free_amount": "",\n        "mail": "newsub2@domain.com",\n        "first_name": "CustomUser",\n        "last_name": "Doe",\n        "address": "221B Baker street",\n        "more_adress": "",\n        "postal_code": "33200",\n        "city": "London",\n        "country": "FR",\n        "originating_view": "StripeView",\n        "originating_parameters": "null"\n      },\n      "mode": "subscription",\n      "payment_intent": null,\n      "payment_link": null,\n      "payment_method_options": {\n      },\n      "payment_method_types": [\n        "card"\n      ],\n      "payment_status": "paid",\n      "phone_number_collection": {\n        "enabled": false\n      },\n      "recovered_from": null,\n      "setup_intent": null,\n      "shipping": null,\n      "shipping_address_collection": null,\n      "shipping_options": [\n\n      ],\n      "shipping_rate": null,\n      "status": "complete",\n      "submit_type": null,\n      "subscription": "sub_1KReZrClnCBJWy556NyE96aD",\n      "success_url": "http://127.0.0.1:8000/donation/success/",\n      "total_details": {\n        "amount_discount": 0,\n        "amount_shipping": 0,\n        "amount_tax": 0\n      },\n      "url": null\n    }\n  },\n  "livemode": false,\n  "pending_webhooks": 3,\n  "request": {\n    "id": "req_kUo0f0axctsHsp",\n    "idempotency_key": "fe759a67-7042-4a78-9a84-f5e9f3833611"\n  },\n  "type": "checkout.session.completed"\n}'
        self.payment_succeeded_sub_cycle_payload = b'{"id": "evt_1KSjThClnCBJWy55RvDvM2ID", "object": "event", "api_version": "2020-08-27", "created": 1644764105, "data": {"object": {"id": "in_1KSiRPClnCBJWy55vfLAQE6q", "object": "invoice", "account_country": "FR", "account_name": "Mobilitains.fr", "account_tax_ids": null, "amount_due": 1100, "amount_paid": 1100, "amount_remaining": 0, "application_fee_amount": null, "attempt_count": 1, "attempted": true, "auto_advance": false, "automatic_tax": {"enabled": false, "status": null}, "billing_reason": "subscription_cycle", "charge": "ch_3KSjTfClnCBJWy551eZiPYH8", "collection_method": "charge_automatically", "created": 1644760119, "currency": "eur", "custom_fields": null, "customer": "cus_L7uOLpyHjoItiF", "customer_address": {"city": null, "country": "FR", "line1": null, "line2": null, "postal_code": null, "state": null}, "customer_email": "newsub2@domain.com", "customer_name": "CustomUser", "customer_phone": null, "customer_shipping": null, "customer_tax_exempt": "none", "customer_tax_ids": [], "default_payment_method": null, "default_source": null, "default_tax_rates": [], "description": null, "discount": null, "discounts": [], "due_date": null, "ending_balance": 0, "footer": null, "hosted_invoice_url": "https://invoice.stripe.com/i/acct_1F7erSClnCBJWy55/test_YWNjdF8xRjdlclNDbG5DQkpXeTU1LF9MOTBTQkVCOTRabU1pdWtKa2w4UWZCeG82V0poU0RJLDM1MzA0OTA102002mGsl6TY?s=ap", "invoice_pdf": "https://pay.stripe.com/invoice/acct_1F7erSClnCBJWy55/test_YWNjdF8xRjdlclNDbG5DQkpXeTU1LF9MOTBTQkVCOTRabU1pdWtKa2w4UWZCeG82V0poU0RJLDM1MzA0OTA102002mGsl6TY/pdf?s=ap", "last_finalization_error": null, "lines": {"object": "list", "data": [{"id": "il_1KSiRPClnCBJWy55PZCYwH6r", "object": "line_item", "amount": 1100, "currency": "eur", "description": "1 \\u00d7 recurring_donation_11eur_daily (at \\u20ac11.00 / day)", "discount_amounts": [], "discountable": true, "discounts": [], "livemode": false, "metadata": {}, "period": {"end": 1644846476, "start": 1644760076}, "plan": {"id": "price_1K8mC3ClnCBJWy55lTSXrRVF", "object": "plan", "active": true, "aggregate_usage": null, "amount": 1100, "amount_decimal": "1100", "billing_scheme": "per_unit", "created": 1640007983, "currency": "eur", "interval": "day", "interval_count": 1, "livemode": false, "metadata": {}, "nickname": null, "product": "prod_KoP0cl9BVnxJj0", "tiers_mode": null, "transform_usage": null, "trial_period_days": null, "usage_type": "licensed"}, "price": {"id": "price_1K8mC3ClnCBJWy55lTSXrRVF", "object": "price", "active": true, "billing_scheme": "per_unit", "created": 1640007983, "currency": "eur", "livemode": false, "lookup_key": null, "metadata": {}, "nickname": null, "product": "prod_KoP0cl9BVnxJj0", "recurring": {"aggregate_usage": null, "interval": "day", "interval_count": 1, "trial_period_days": null, "usage_type": "licensed"}, "tax_behavior": "unspecified", "tiers_mode": null, "transform_quantity": null, "type": "recurring", "unit_amount": 1100, "unit_amount_decimal": "1100"}, "proration": false, "quantity": 1, "subscription": "sub_1K8mDYClnCBJWy550o3yYM4G", "subscription_item": "si_KoP1S4GnXx8an2", "tax_amounts": [], "tax_rates": [], "type": "subscription"}], "has_more": false, "total_count": 1, "url": "/v1/invoices/in_1KSiRPClnCBJWy55vfLAQE6q/lines"}, "livemode": false, "metadata": {}, "next_payment_attempt": null, "number": "39BA8C9C-0056", "on_behalf_of": null, "paid": true, "paid_out_of_band": false, "payment_intent": "pi_3KSjTfClnCBJWy55128oX3OW", "payment_settings": {"payment_method_options": null, "payment_method_types": null}, "period_end": 1644760076, "period_start": 1644673676, "post_payment_credit_notes_amount": 0, "pre_payment_credit_notes_amount": 0, "quote": null, "receipt_number": null, "starting_balance": 0, "statement_descriptor": null, "status": "paid", "status_transitions": {"finalized_at": 1644764103, "marked_uncollectible_at": null, "paid_at": 1644764103, "voided_at": null}, "subscription": "sub_1K8mDYClnCBJWy550o3yYM4G", "subtotal": 1100, "tax": null, "total": 1100, "total_discount_amounts": [], "total_tax_amounts": [], "transfer_data": null, "webhooks_delivered_at": 1644760119}}, "livemode": false, "pending_webhooks": 1, "request": {"id": null, "idempotency_key": null}, "type": "invoice.payment_succeeded"}'

    def _get_signature(self, payload):
        # # https://stripe.com/docs/webhooks/signatures#prepare-payload
        decoded_payload = payload.decode("utf-8")
        signed_payload = f"{self.timestamp}.{decoded_payload}"
        expected_signature = WebhookSignature._compute_signature(
            signed_payload, settings.STRIPE_ENDPOINT_SECRET
        )

        return expected_signature

    def post_payload_to_webhook(self, payload):
        expected_signature = self._get_signature(payload)
        request = self.factory.post(
            reverse("stripe_app:webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=(
                f"t={self.timestamp},"
                f"v1={expected_signature}"
                ",v0=placeholder"
            ),
        )
        response = stripe_webhook(request)
        return response

    def test_new_sub_registration(self):
        """Test that an unique Stripe checkout.session.completed event
        is properly saved.
        """
        response = self.post_payload_to_webhook(
            self.checkout_session_completed_sub_payload
        )
        self.assertEqual(response.status_code, 200)

        number_of_donations = Donation.objects.count()
        self.assertEqual(number_of_donations, 1)

    def test_duplicate_checkout_completed_handling(self):
        """Test that a duplicate Stripe checkout.session.completed event
        is ignored."""

        self.test_new_sub_registration()
        response = self.post_payload_to_webhook(
            self.checkout_session_completed_sub_payload
        )

        self.assertEqual(response.status_code, 500)

        number_of_donations = Donation.objects.count()
        self.assertEqual(number_of_donations, 1)

    def test_sub_cycle_save(self):
        """Test that recurring payments are saved"""

        # First donation
        self.test_new_sub_registration()

        # POST a payment_succeeded event for the same subscription
        # for the recurring payment (the next month)
        response = self.post_payload_to_webhook(
            self.payment_succeeded_sub_cycle_payload
        )
        self.assertEqual(response.status_code, 200)

        # 1 is the original donation, 2 is the recurring donation
        number_of_donations = Donation.objects.count()
        self.assertEqual(number_of_donations, 2)

    def test_sub_cycle_save_duplicate(self):
        """Test that a duplicate Stripe payment_succeeded event
        is ignored."""

        # Initial donation
        self.post_payload_to_webhook(
            self.checkout_session_completed_sub_payload
        )
        # The first recurring payment
        self.post_payload_to_webhook(self.payment_succeeded_sub_cycle_payload)
        # The exact same event, with the same id.
        response = self.post_payload_to_webhook(
            self.payment_succeeded_sub_cycle_payload
        )

        self.assertEqual(response.status_code, 200)

        number_of_donations = Donation.objects.count()
        self.assertEqual(number_of_donations, 2)

    def test_donation_page_status_code(self):
        """Test that the donation pages returns a 200 status code."""
        response = self.client.get(reverse("stripe_app:stripe"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("stripe_app:stripe_success"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("stripe_app:quick_donation", args=[1])
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("stripe_app:get_public_key"))
        self.assertEqual(response.status_code, 200)

    def test_signature_check(self):
        """Test the signature error handling"""
        self._get_signature(self.checkout_session_completed_sub_payload)

        # We include a wrong signature in the header
        request = self.factory.post(
            reverse("stripe_app:webhook"),
            data=self.checkout_session_completed_sub_payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=(
                f"t={self.timestamp}," f"v1=wrong_signature," f"v0=placeholder"
            ),
        )
        response = stripe_webhook(request)
        self.assertEqual(response.status_code, 400)

        # We don't include the signature in the payload
        request = self.factory.post(
            reverse("stripe_app:webhook"),
            data=self.checkout_session_completed_sub_payload,
            content_type="application/json",
        )

        response = stripe_webhook(request)
        self.assertEqual(response.status_code, 400)

    def test_payload_check(self):
        """Test the payload error handling"""
        payload = self.checkout_session_completed_sub_payload
        # Alter the payload to cause a value error
        payload = payload.decode("utf-8")
        payload = payload.replace('"id":', "wrong-id")
        payload = payload.encode("utf-8")

        response = self.post_payload_to_webhook(payload)
        self.assertEqual(response.status_code, 400)

    def test_checkout_session_expired(self):
        """Test the session expired handling"""

        payload = self.checkout_session_completed_sub_payload
        # Alter payload to get a session expired type
        payload = payload.decode("utf-8")
        payload = payload.replace(
            '"type": "checkout.session.completed"',
            '"type": "checkout.session.expired"',
        )
        payload = payload.encode("utf-8")

        response = self.post_payload_to_webhook(payload)
        self.assertEqual(response.status_code, 200)

    def test_unknown_event(self):
        """Test the unknown event handling"""

        payload = self.checkout_session_completed_sub_payload
        # Alter payload to get a session expired type
        payload = payload.decode("utf-8")
        payload = payload.replace(
            '"type": "checkout.session.completed"', '"type": "unknown_event"'
        )
        payload = payload.encode("utf-8")

        response = self.post_payload_to_webhook(payload)
        self.assertEqual(response.status_code, 500)


class TestStripeAppSelenium(LiveServerTestCase):
    """Regroups all tests done with Selenium"""

    def setUp(self):

        self.options = Options()
        self.options.add_argument("--headless")
        self.browser = WebDriver(
            ChromeDriverManager().install(), chrome_options=self.options
        )
        # Introduce a delay to let the browser load the pages
        # see doc :
        # https://www.selenium.dev/documentation/webdriver/waits/#implicit-wait
        self.browser.implicitly_wait(3)
        self.this_dir = Path(__file__).parent.absolute()

    def tearDown(self):
        self.browser.quit()

    def fill_personal_info_part(self):
        """Fill the personal info part of the form"""
        self.browser.find_element_by_id("id_first_name").send_keys("FirstName")
        self.browser.find_element_by_id("id_last_name").send_keys("LastName")
        self.browser.find_element_by_id("id_mail").send_keys("email@email.com")
        self.browser.find_element_by_id("id_address").send_keys("Address")
        self.browser.find_element_by_id("id_more_address").send_keys(
            "Complement"
        )
        self.browser.find_element_by_id("id_postal_code").send_keys("12345")
        self.browser.find_element_by_id("id_city").send_keys("City")
        # Check the consent box
        self.browser.find_element_by_css_selector(
            "label[for='id_data_collect']"
        ).click()

    def fill_amount_form_sub_20euros(self):
        """Fill the amount form with a monthly sub of 20 euros"""
        # Select "Je donne tous les mois"
        self.browser.find_element_by_css_selector(
            "label[for='id_donation_type_1']"
        ).click()
        # Select '20€'
        self.browser.find_element_by_css_selector(
            "label[for='subscription_amount_rb_2']"
        ).click()

    def fill_amount_form_onetime_preset_amount(self):
        """Fill the amount form with a one time payment"""
        # Select "Je donne une fois"
        self.browser.find_element_by_css_selector(
            "label[for='id_donation_type_0']"
        ).click()
        # Select the 2nd choice (preset amount)
        self.browser.find_element_by_css_selector(
            "label[for='payment_amount_rb_1']"
        ).click()

    def fill_amount_form_onetime_free_amount(self):
        """Fill the amount form with a one time payment"""
        # Select "Je donne une fois"
        self.browser.find_element_by_css_selector(
            "label[for='id_donation_type_0']"
        ).click()
        # Select the 4th choice (free amount)
        self.browser.find_element_by_css_selector(
            "label[for='payment_amount_rb_1']"
        ).click()
        # Fill the free amount
        self.browser.find_element_by_id("free_amount").send_keys("15")

    def run_stripe_page_javascript(self):
        """Runs the javascripts in Stripe page"""
        self.browser.execute_script(
            open(
                self.this_dir / "static" / "stripe_app" / "form_flow.js"
            ).read()
        )
        self.browser.execute_script(
            open(
                self.this_dir / "static" / "stripe_app" / "form_style.js"
            ).read()
        )
