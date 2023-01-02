import datetime
import json
import logging
import random
import string

import stripe
import user_agents
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.http.response import HttpResponseServerError
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from mailing_list.events import subscribe_user_to_list
from mailing_list.models import MailingList
from topicblog.models import SendRecordTransactionalAdHoc
from transport_nantes.settings import (
    ROLE,
    STRIPE_ENDPOINT_SECRET,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_SECRET_KEY,
)

from .forms import AmountForm, DonationForm, QuickDonationForm
from .models import Donation, TrackingProgression

logger = logging.getLogger("django")


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
        amount_form = AmountForm()
        amount_form.fields["payment_amount"].choices = get_amount_choices()
        amount_form.fields[
            "subscription_amount"
        ].choices = get_subscription_amounts()  # noqa
        context = {}
        context["info_form"] = DonationForm()
        context["amount_form"] = amount_form
        context["originating_view"] = "StripeView"

        return render(request, self.template_name, context)


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
    if ROLE == "production":
        subscription_choices = [
            ("price_1JKfNuClnCBJWy55SxZWROd3", "5 euros"),
            ("price_1IIGzvClnCBJWy55MCIEkMpE", "10 euros"),
            ("price_1JKfOBClnCBJWy55LX4ctrrc", "15 euros"),
            ("price_1JKfOVClnCBJWy55HGa9OXcz", "20 euros"),
        ]
    else:
        subscription_choices = [
            ("price_1J0of7ClnCBJWy551iIQ6ydg", "8 euros"),
            ("price_1J0ogXClnCBJWy552i9Bs2bg", "12 euros"),
            ("price_1J0ohVClnCBJWy55dAJxHjXE", "20 euros"),
            ("price_1JKgKtClnCBJWy55Ob7PeJs8", "30 euros"),
        ]
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

    amount_choices = [
        (5, "5 euros"),
        (10, "10 euros"),
        (25, "25 euros"),
        (0, "Montant libre"),
    ]
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
            if request.POST["donation_type"] == "payment":
                checkout_session = stripe.checkout.Session.create(
                    # Links need to be valid
                    # Cant't use bare /donation, will raise an error.
                    success_url=domain_url + "/donation/success/",
                    cancel_url=domain_url + "/donation/",
                    payment_method_types=["card"],
                    mode=request.POST["donation_type"],
                    customer_email=request.POST["mail"],
                    line_items=[
                        {
                            "name": "Donation",
                            "quantity": 1,
                            "currency": "eur",
                            # Amount in cents
                            "amount": order_amount(request.POST),
                        }
                    ],
                    # Metadata is an optional field containing all personal
                    # informations gathered in the form.
                    metadata=request.POST,
                )
                return JsonResponse({"sessionId": checkout_session["id"]})

            # There are fewer parameters for subscription because some of them
            # are set on Stripe's Dashboard.
            # Subscriptions are created in the dashboard only.
            elif request.POST["donation_type"] == "subscription":
                checkout_session = stripe.checkout.Session.create(
                    # Links need to be valid
                    success_url=domain_url + "/donation/success/",
                    cancel_url=domain_url + "/donation/",
                    payment_method_types=["card"],
                    mode=request.POST["donation_type"],
                    customer_email=request.POST["mail"],
                    line_items=[
                        {
                            "quantity": 1,
                            # product id from Stripe's Dashboard.
                            # Exemple : price_1J0of7ClnCBJWy551iIQ6ydg
                            # Hardcoded in get_subscription_amounts()
                            "price": request.POST["subscription_amount"],
                        }
                    ],
                    metadata=request.POST,
                )
                return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as error_message:
            logger.error(error_message)
            return JsonResponse({"error": "Echec de la création de la session"})


def order_amount(items: dict) -> int:
    """
    Take the donation amount (in euros) in returns it in centimes.

    items: content of request.POST
    """

    # "0" indicates that user selected "Montant libre"
    if items["payment_amount"] == "0":
        # "Free amount" field is a string input by user in the form.
        # The form wont let non numeric values be entered.
        free_amount = float(items["free_amount"])
        free_amount_in_cents = int(free_amount * 100)
        return free_amount_in_cents
    else:
        selected_payment_amount = float(items["payment_amount"])
        selected_payment_amount_in_cents = int(selected_payment_amount * 100)
        return selected_payment_amount_in_cents


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

    Also saves the user agent information for eventual analysis.
    """
    try:
        data = request.POST
        data = data.dict()
        for key, _ in data.items():
            if data[key] == "true":
                data[key] = True
            elif data[key] == "false":
                data[key] = False

        user_agent = user_agents.parse(request.META.get("HTTP_USER_AGENT"))

        kwargs = {
            "amount_form_done": data["step_1_completed"],
            "donation_form_done": data["step_2_completed"],
            "tn_session": request.session.get("tn_session"),
            "browser": user_agent.browser.family,
            "browser_version": user_agent.browser.version_string,
            "os": user_agent.os.family,
            "os_version": user_agent.os.version_string,
            "device_family": user_agent.device.family,
            "device_brand": user_agent.device.brand,
            "device_model": user_agent.device.model,
            "is_mobile": user_agent.is_mobile,
            "is_tablet": user_agent.is_tablet,
            "is_touch_capable": user_agent.is_touch_capable,
            "is_pc": user_agent.is_pc,
            "is_bot": user_agent.is_bot,
        }

        try:
            data = TrackingProgression(**kwargs)
            data.save()
        except Exception as error_message:
            logger.info(
                "Error while creating TrackingProgression instance : {0}",
                error_message,
            )

        return HttpResponse(status=200)
    except Exception as error_message:
        logger.info(f"error message: {error_message}")
        return JsonResponse({"error": str(error_message)})


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
    logger.info("Stripe webhook called")
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    logger.info(f"payload: {payload}")
    try:
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    except KeyError:
        logger.info("HTTP_STRIPE_SIGNATURE not present in request")
        return HttpResponse(status=400)
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        logger.info("Invalid payload in strip webhook")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.info("Invalid signature in stripe webhook")
        return HttpResponse(status=400)

    logger.info(f"The event has been constructed : {event}")
    logger.info(f"The event type is : {event['type']}")
    # Event when a donor completes a checkout session
    # whether it's a one-time payment or a subscription.
    if event["type"] == "checkout.session.completed":
        logger.info("Stripe payment webhook succeeded.")
        logger.info(
            "Details attached to event : \n\n" + "=" * 30 + f"\n {event}"
        )
        try:
            donation = make_donation_from_webhook(event)
            donation.save()
        except Exception as error_message:
            logger.error(
                "=" * 80
                + f"\nError while creating \
            a new Donation. Details : {error_message}"
            )
            return HttpResponse(status=500)
        update_user_name(event)
        send_thank_you_email(event)

    # Event for subscription payments (initial or recurring)
    # cf https://stripe.com/docs/billing/subscriptions/webhooks#tracking
    elif event["type"] == "invoice.payment_succeeded":
        # subscription_cycle is the reason invoked for subscription payments
        # that are not the first one.
        billing_reason = event["data"]["object"]["billing_reason"]
        logger.info(f"Billing reason : {billing_reason}")
        if event["data"]["object"]["billing_reason"] == "subscription_cycle":
            logger.info("Stripe subscription payment webhook called.")
            logger.info(
                "Details attached to event : \n\n" + "=" * 30 + f"\n {event}"
            )
            customer_id = event["data"]["object"]["customer"]
            amount = int(event["data"]["object"]["amount_due"])
            event_id = event["id"]
            try:
                save_recurring_payment_details(customer_id, amount, event_id)
            except Exception as e:
                logger.info(f"Recurring payment couldn't be processed : {e}")

            return HttpResponse(status=200)

    elif event["type"] == "checkout.session.expired":
        logger.info("Stripe checkout session expired")
        logger.info(
            "Details attached to event : \n\n" + "=" * 30 + f"\n {event}"
        )
        try:
            donation = make_donation_from_webhook(event)
            donation.amount_centimes_euros = 0
            donation.save()
        except Exception as error_message:
            logger.error(
                "=" * 80
                + f"\nError while creating \
            a new Donation. Details : {error_message}"
            )
            return HttpResponse(status=500)
        update_user_name(event)

    else:
        logger.error(f"Unknown event type : {event['type']}")
        logger.error(
            "Details attached to event : \n\n" + "=" * 30 + f"\n{event}"
        )
        return HttpResponse(status=500)

    return HttpResponse(status=200)


def get_random_string(length=20) -> str:
    """
    Returns a random string of length "length"
    This random string will be used as username value to
    create a new user in get_user(email) function.
    """
    random_string = "".join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length)
    )  # noqa
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
        logger.info(f"User already exists: {str(existing_users)}")
        return existing_users[0]

    else:
        user = User()
        user.email = email
        user.username = get_random_string(20)
        user.is_active = False
        user.save()
        return user


def update_user_name(event: dict) -> None:
    """

    Name user if unnamed.

    If the user has no first or last name, provide them.
    If either exists, however, we should respect them.

    This is for instances where the user provides a name without
    meaning to edit her/his user profile.  For example, if the user
    intends to be called "Joe", we shouldn't take a legal name
    attached to a bank card and start saying "Hello, Joseph".
    """
    try:
        user = get_user(event["data"]["object"]["customer_email"])
        if user.first_name == "" and user.last_name == "":
            metadata = event["data"]["object"]["metadata"]
            user.first_name = metadata["first_name"]
            user.last_name = metadata["last_name"]
            user.save()
    except Exception as error_message:
        logger.info(f"Error while updating user name : {error_message}")


def make_donation_from_webhook(event: dict) -> Donation:
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

    metadata = event["data"]["object"]["metadata"]
    # kwargs to be used to create a Donation object.
    kwargs = {
        "stripe_event_id": event["id"],
        "stripe_customer_id": event["data"]["object"]["customer"],
        "user": get_user(event["data"]["object"]["customer_email"]),
        "email": event["data"]["object"]["customer_email"],
        "first_name": metadata["first_name"],
        "last_name": metadata["last_name"],
        "address": metadata["address"],
        "more_address": metadata["more_adress"],
        "postal_code": metadata["postal_code"],
        "city": metadata["city"],
        "country": metadata["country"],
        "periodicity_months": mode,
        "amount_centimes_euros": int(event["data"]["object"]["amount_total"]),
        "originating_view": metadata["originating_view"],
        "originating_parameters": metadata["originating_parameters"],
    }
    try:
        if kwargs.get("user") is None:
            raise Exception("User not found.")
        logger.info(f"Adding {kwargs['user']} to donors mailing list...")
        add_user_to_donor_mailing_list(user=kwargs["user"])
    except Exception as e:
        logger.error(f"Error while adding user to donors' mailing list : {e}")
        # We don't want to stop the process if the mailing list
        # couldn't be updated.

    logger.info("Creating donation...")
    try:
        already_exists = Donation.objects.filter(
            stripe_event_id=event["id"]
        ).exists()
        if already_exists:
            logger.info("Donation already exists.")
            raise Exception(
                "This event has already been processed. Event : " + event["id"]
            )
        else:
            donation = Donation(**kwargs)
            logger.info("Donation entry created.")
            return donation
    except Exception as e:
        logger.error(f"Error while creating a new donation : {e}")
        # This error is serious enough for us to propagate the error
        raise


def add_user_to_donor_mailing_list(user: User) -> None:
    this_year = str(datetime.date.today().year)
    this_year_donors_mailing_list, _ = MailingList.objects.get_or_create(
        mailing_list_token="donors-" + this_year,
        mailing_list_type="DONORS",
        defaults={
            "mailing_list_name": this_year + "'s donors list",
            "mailing_list_token": "donors-" + this_year,
            "contact_frequency_weeks": 12,
            "list_active": True,
            "mailing_list_type": "DONORS",
        },
    )
    subscribe_user_to_list(user, this_year_donors_mailing_list)


def save_recurring_payment_details(
    customer_id: str, amount: int, event_id: str
) -> None:
    """
    Save a donation entry for recurring payments.
    We use the data of the last donation associated with the
    stripe_customer_id to create a new one.
    This happens when a donor did subscribe to a monthly donation
    and the next payments are successful.
    """
    logger.info("Saving recurring payment details...")
    # We're getting the last record of a subscription to have
    # the proper amount and periodicity.
    customer = Donation.objects.filter(
        stripe_customer_id=customer_id,
        # __gte is greater than or equal to
        periodicity_months__gte=1,
    ).last()

    if customer is None:
        logger.info(
            f"No subscriptions found for this customer_id: ({customer_id})"
        )
        raise Exception("No subscriptions found for this customer_id.")

    last_donation_kwargs = customer.__dict__

    kwargs = {
        "stripe_event_id": event_id,
        "stripe_customer_id": last_donation_kwargs["stripe_customer_id"],
        "user_id": last_donation_kwargs["user_id"],
        "email": last_donation_kwargs["email"],
        "first_name": last_donation_kwargs["first_name"],
        "last_name": last_donation_kwargs["last_name"],
        "address": last_donation_kwargs["address"],
        "more_address": last_donation_kwargs["more_address"],
        "postal_code": last_donation_kwargs["postal_code"],
        "city": last_donation_kwargs["city"],
        "country": last_donation_kwargs["country"],
        "periodicity_months": last_donation_kwargs["periodicity_months"],
        "amount_centimes_euros": amount,
        "originating_view": "<repeat-subscription>",
        "originating_parameters": "",
        "timestamp": datetime.datetime.now,
    }

    try:
        already_exists = Donation.objects.filter(
            stripe_event_id=event_id
        ).exists()

        if already_exists:
            logger.info("Event already saved : " + event_id)
            raise Exception
        else:
            new_donation = Donation(**kwargs)
            new_donation.save()
            logger.info("Donation entry created.")
    except Exception as e:
        logger.info(f"Error while creating a new donation : {e}")
        raise Exception


def send_thank_you_email(
    event: dict,
) -> None:
    """
    Send a thank you email to the donor.
    """
    logger.info("Preparing thank you email...")
    try:
        user = get_user(event["data"]["object"]["customer_email"])
        send_record = SendRecordTransactionalAdHoc.objects.create(
            recipient=user
        )
        custom_email = prepare_email(user.email, send_record=send_record)
        logger.info(f"Sending thank you email to {user.email}...")
        custom_email.send()
        logger.info("Thank you email sent.")
        send_record.handoff_time = datetime.datetime.now(datetime.timezone.utc)
        send_record.save()

    except Exception as e:
        logger.error(f"Error while sending thank you email : {e}")
        send_record.status = "FAILED"
        send_record.save()


def prepare_email(
    email: str, send_record: SendRecordTransactionalAdHoc
) -> EmailMultiAlternatives:
    """Create a sendable Email object"""
    template = "stripe_app/thank_you_email.html"
    context = {}
    html_message = render_to_string(template, context=context)
    values_to_pass_to_ses = {
        "send_record class": send_record.__class__.__name__,
        "send_record id": str(send_record.id),
    }
    comments_header = json.dumps(values_to_pass_to_ses)
    headers = {
        "X-SES-CONFIGURATION-SET": settings.AWS_CONFIGURATION_SET_NAME,
        "Comments": comments_header,
    }
    email = EmailMultiAlternatives(
        subject="Merci pour votre don !",
        body=render_to_string(template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        headers=headers,
    )
    email.attach_alternative(html_message, "text/html")

    return email


class QuickDonationView(TemplateView):
    """
    Displays a simplified Donation form with a given
    amount in Euros.
    """

    template_name = "stripe_app/donation_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The amount is set in the URL.
        # If no amount is set, StripeView is fired instead.
        context["amount_form"] = QuickDonationForm(
            initial={"amount": self.kwargs["amount"]}
        )
        context["info_form"] = DonationForm()
        context["originating_view"] = "QuickDonationView"
        return context
