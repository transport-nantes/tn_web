from collections import Counter
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Tuple, Type, Union, TYPE_CHECKING
from django.apps import apps
from django.conf import settings
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError

from django.db.models import Count, Max
from django.dispatch import receiver
from django.http import (Http404, HttpResponseBadRequest,
                         HttpResponseServerError, FileResponse)
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.decorators import permission_required as perm_required
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, BaseFormView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse, reverse_lazy, resolve
from django.utils.html import strip_tags
from django_ses.signals import (open_received, click_received,
                                send_received)

from asso_tn.utils import StaffRequired, make_timed_token, token_valid
from mailing_list.events import (get_subcribed_users_email_list,
                                 user_subscribe_count)
from mailing_list.models import MailingList

from .models import (SendRecordTransactionalEmail,
                     SendRecordTransactionalPress, TopicBlogItem,
                     TopicBlogEmail, TopicBlogMailingListPitch,
                     TopicBlogPress, TopicBlogLauncher,
                     SendRecordMarketingEmail, SendRecordMarketingPress,
                     SendRecordTransactional, TopicBlogWrapper)
from .forms import (TopicBlogItemForm, TopicBlogEmailSendForm,
                    TopicBlogLauncherForm, TopicBlogEmailForm,
                    TopicBlogMailingListPitchForm, TopicBlogPressForm,
                    SendToSelfForm, TopicBlogWrapperForm)

# Doesn't actually import at runtime, it's for type hinting
if TYPE_CHECKING:
    from .models import TopicBlogObjectBase
    from django.views.generic import View


logger = logging.getLogger("django")


class TopicBlogBaseEdit(LoginRequiredMixin, FormView):
    """
    Create or modify a concrete TBObject.  This class handles the
    elements common to all TBObject types.

    Fetch a TopicBlogObject and render it for editing.  For additional
    security (avoid phishing), require the pk_id and slug.  If the
    slug is absent, assume it is empty.  If the pk_id is also absent,
    we are creating a new item.

    The derived view must provide model, template_name, and form_class.

    """
    login_url = reverse_lazy("authentication:login")
    template_name = 'topicblog/topicblogbase_edit.html'

    def get_context_data(self, **kwargs):
        # In FormView, we must use the self.kwargs to retrieve the URL
        # parameters. This stems from the View class that transfers
        # the URL parameters to the View instance and assigns kwargs
        # to self.kwargs.
        pk_id = self.kwargs.get('pkid', -1)
        slug = self.kwargs.get('the_slug', '')
        if pk_id > 0:
            tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)
            kwargs["form"] = kwargs.get(
                "form",
                self.form_class(instance=tb_object))
            context = super().get_context_data(**kwargs)
        else:
            tb_object = self.model()
            context = super().get_context_data(**kwargs)
        context['tb_object'] = tb_object
        context["slug_fields"] = tb_object.get_slug_fields()
        context["model_name"] = self.model.__name__
        context = self.fill_form_tabs(context)
        return context

    def fill_form_tabs(self, context: dict) -> dict:
        """Pass to context only the appropriate forms
        e.g., if a form doesn't have any of the "form_content_b"'s fields
        the form_content_b wont be displayed.
        """
        form = self.form_class()
        possible_forms = {
            "form_admin": [
                "slug", "subject", "title", "template_name", 'template',
                "header_title", "header_description", "header_image",
                "mailing_list", "article_slug", "campaign_name",
                "underlying_slug", "original_model",
            ],
            "form_content_a": [
                "body_text_1_md", "cta_1_slug", 'body_image',
                'body_image_alt_text', "cta_1_label", "body_image_1",
                "body_image_1_alt_text", "headline", "launcher_text_md",
                "launcher_image", "launcher_image_alt_text", "teaser_chars",
                "subscription_form_title", "subscription_form_button_label",
                "body_text_2_md", "cta_2_slug", "cta_2_label",
            ],
            "form_content_b": [
                "body_image_2", "body_image_2_alt_text", 'body_text_3_md',
                'cta_3_slug', 'cta_3_label',
            ],
            "form_social": ["social_description", "twitter_title",
                            "twitter_description", "twitter_image",
                            "og_title", "og_description", "og_image",
                            "mail_only_contact_info"],
            "form_notes": ["author_notes"]
        }
        # Other fields is a catch-all that gets every field that should
        # be included but isn't because not sorted in the get_context_data
        # function
        other_fields = []
        # Add to context only the necessary forms
        for form_field_name, _ in form.fields.items():
            field_found = False
            for form_name, _ in possible_forms.items():
                if form_field_name in possible_forms[form_name]:
                    context[form_name] = possible_forms[form_name]
                    field_found = True
                    break
            if not field_found:
                print("not found:", form_field_name)
                other_fields.append(form_field_name)

        if other_fields:
            context["form_others"] = other_fields

        return context

    def form_valid(self, form):
        tb_object = form.save(commit=False)
        tb_object.user = User.objects.get(username=self.request.user)

        # Read-only fields aren't set, so we have to fetch them
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            tb_existing = self.model.objects.get(id=pkid)
            tb_object.first_publication_date = \
                tb_existing.first_publication_date
        else:
            tb_existing = None
        if hasattr(self, "form_post_process"):
            tb_object = self.form_post_process(tb_object, tb_existing, form)

        # Every modification creates a new item.
        tb_object.pk = None
        tb_object.publication_date = None
        tb_object.save()
        return HttpResponseRedirect(tb_object.get_absolute_url())


class TopicBlogBaseView(TemplateView):
    """
    Render a TopicBlogItem.

    View a TopicBlogObject by published slug.  No authentication
    required.

    The derived view must provide model.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            tb_object = self.model.objects.filter(
                slug=kwargs['the_slug'],
                publication_date__isnull=False
            ).order_by("publication_date").last()
        except ObjectDoesNotExist:
            raise Http404("Page non trouvée")
        if tb_object is None:
            raise Http404("Page non trouvée")

        servable = tb_object.get_servable_status()
        if not servable:
            logger.info("TopicBlogBaseView: %s is not servable", tb_object)
            raise HttpResponseServerError("Le serveur a rencontré un problème")

        # The template is set in the model, it's a str referring to an
        # existing template in the app.
        self.template_name = tb_object.template_name
        context['page'] = tb_object
        tb_object: self.model  # Type hint for linter
        context = tb_object.set_social_context(context)

        return context


class TopicBlogBaseViewOne(LoginRequiredMixin, TemplateView):
    """
    Render a specific TopicBlogObject.

    The pk_id specifies which object we want.  A slug is an additional
    security measure to prevent probing by pk_id.  If the slug is not
    provided, it is interpreted to be empty, which only makes sense
    during object creation.

    The derived view must provide model.

    """

    transactional_send_record_class = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk_id = kwargs.get('pkid', -1)
        slug = kwargs.get('the_slug', '')
        tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)

        # We check that the object's template is valid and configured, or
        # raise a 500 error.
        if tb_object.template_name in tb_object.template_config:
            self.template_name = tb_object.template_name
        else:
            logger.error(
                f"Current template ({tb_object.template_name}) is not configured.")
            logger.debug(f"Template config: {tb_object.template_config}"
                         f"\nTemplate name: {tb_object.template_name}"
                         f"\nObject ID : {tb_object.id}"
                         f"\nObject class : {tb_object.__class__.__name__}")
            raise ImproperlyConfigured(
                f"Template {tb_object.template_name} is not configured")

        context['page'] = tb_object
        context = tb_object.set_social_context(context)
        context['topicblog_admin'] = True
        context["base_model"] = self.model.__name__.lower()

        context["served_object"] = self.model.objects.filter(
            slug=slug,
            publication_date__isnull=False
        ).order_by("publication_date").last()

        if self.transactional_send_record_class:
            context["transactional_send_record_class"] = \
                self.transactional_send_record_class.__name__
        return context

    def post(self, request, *args, **kwargs):
        pk_id = kwargs.get('pkid', -1)
        the_slug = kwargs.get('the_slug', '')
        tb_object = get_object_or_404(self.model, id=pk_id, slug=the_slug)

        user = User.objects.get(username=request.user)
        if tb_object.user == user:
            if not user.has_perm('topicblog.may_publish_self'):
                raise PermissionDenied("Vous n'avez pas les droits pour "
                                       "publier vos propres articles")
        try:
            tb_object.publisher = self.request.user
            if tb_object.publish():
                tb_object.save()
                return HttpResponseRedirect(tb_object.get_absolute_url())
        except Exception as e:
            logger.error(e)
            logger.error(f"Failed to publish object {pk_id} with" +
                         "slug \"{the_slug}\"")
            return HttpResponseServerError("Failed to publish item")
        # This shouldn't happen.  It's up to us to make sure we've
        # vetted that the user is authorised to publish and that the
        # necessary fields are completed before enabling the publish
        # button.  Therefore, a 500 is appropriate here.
        return HttpResponseServerError()


class TopicBlogBaseList(LoginRequiredMixin, ListView):
    """
    Render a list of TopicBlogObjects.

    """
    login_url = reverse_lazy("authentication:login")

    def get_context_data(self, **kwargs):
        """This is a GET, supply the context."""
        context = super().get_context_data(**kwargs)
        qs = context['object_list']
        the_slug = self.kwargs.get('the_slug', None)
        if the_slug:
            context['slug'] = the_slug
            context['servable_object'] = qs.filter(
                publication_date__lte=datetime.now(timezone.utc)).order_by(
                    '-publication_date').first()
        context["new_object_url"] = self.model.new_object_url
        context["listone_object_url"] = self.model.listone_object_url
        context["listall_object_url"] = self.model.listall_object_url
        context["viewbyslug_object_url"] = self.model.viewbyslug_object_url

        return context

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of matches for a given the_slug."""
        qs = super(ListView, self).get_queryset(*args, **kwargs)
        if 'the_slug' in self.kwargs:
            # If we have a slug, show it.
            the_slug = self.kwargs['the_slug']

            # Clean up old objects.  This should perhaps be pushed to
            # celery later.
            mark_moribund_and_delete(qs.filter(slug=the_slug))

            the_qs = qs.filter(slug=the_slug).order_by('-date_created')
            return the_qs

        # If we don't have a slug, list all slugs.
        return qs.values('slug') \
                 .annotate(count=Count('slug'),
                           date_created=Max('date_created'),
                           publication_date=Max('publication_date')) \
                 .order_by('-date_created')

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicblogbase_list_one.html'] + names
        else:
            return ['topicblog/topicblogbase_list.html'] + names


# This is the name of the key we put in contexts to communicate
# to renderers.
k_render_as_email = "render_as_email"


class SendableObjectMixin:
    """ Define the sending by email behaviour for TopicBlog Objects """

    # Defines the concrete subclass of SendRecordBase that we use to
    # record this sending operation.
    send_record_class = None
    # Defines the concrete subclass of sendable that we are treating.
    base_model: Type['TopicBlogObjectBase'] = None

    def get_last_published_email(self, tb_slug: str) -> base_model:
        """Fetch the currently published email object.

        Fetch the base_model instance in this slug class with most
        recent publication_date.

        """
        tb_objects = self.base_model.objects.filter(
            slug=tb_slug,
            publication_date__isnull=False
        ).order_by('-publication_date')
        if len(tb_objects) == 0:
            logger.error("Failed to find requested email object in class "
                         f"{tb_slug}")
            raise ValueError(
                f"There is no {self.base_model.__name__} with"
                f" slug {tb_slug} and a not-null publication date")
        return tb_objects[0]

    def prepare_email(self, pkid: int, the_slug: str, recipient: list,
                      mailing_list: MailingList, send_record) \
            -> mail.EmailMultiAlternatives:
        """
        Creates a sendable email object from a TBobject with a mail
        client-friendly template, given a pkid, a slug and a mail adress.

        Keyword arguments:
        pkid -- the id of the object to send
        the_slug -- the slug of the object to send
        recipient -- the list of recipients
        mailing_list -- the mailing list to send a the object to
        send_record -- the send_record object associated with the email

        Returns:
        An EmailMultiAlternatives object ready to be sent.
        """
        if pkid < 0 or the_slug is None:
            logger.info(f"pkid < 0 ({pkid}) or slug is none ({the_slug})")
            return HttpResponseServerError()

        # Preparing the email
        tb_email: Union[TopicBlogEmail, TopicBlogPress] = (
            self.base_model.objects.get(pk=pkid, slug=the_slug))
        self.template_name = (
            tb_email.template_config[tb_email.template_name]
            .get('email_template')
        )

        context = self._set_email_context(recipient, send_record.id, tb_email)

        try:
            email = self._create_email_object(tb_email, context, recipient,
                                              send_record)
        except Exception as e:
            message = \
                f"Error while creating EmailMultiAlternatives object: {e}"
            logger.info(message)
            raise Exception(message)

        return email

    def _create_email_object(self, tb_object, context: dict,
                             recipient_list: list, send_record,
                             from_email: str = settings.DEFAULT_FROM_EMAIL) \
            -> mail.EmailMultiAlternatives:
        """Create an EmailMultiAlternatives object.

        To send emails to multiple persons, django send_mail function
        isn't enough, we need to create a EmailMultiAlternatives
        object to be able, for example to put recipients in BCC field
        or add attachments.  **BUG** We probably don't want ever to
        send to a list, since it presents a risk of name leakage (GDPR
        and reputation) and doesn't let us track individual mail
        messages.

        Doc :
        https://docs.djangoproject.com/en/3.2/topics/email/#sending-multiple-emails
        https://docs.djangoproject.com/en/3.2/topics/email/#emailmessage-objects
        https://docs.djangoproject.com/en/3.2/topics/email/#sending-alternative-content-types

        Keyword arguments:
        tb_object -- the TopicBlog object to send
        context -- the context to use to render the email
        recipient_list -- the list of recipients
        from_email -- the sender email address

        Returns:
        An EmailMultiAlternatives object ready to be sent.

        """
        # HTML message is the one displayed in mail client
        html_message = render_to_string(
            self.template_name, context=context, request=self.request)
        # In cases where the HTML message isn't accepted, a plain text
        # message is displayed in the mail client.
        plain_text_message = strip_tags(html_message)

        # AWS SES reads the headers to check the presence of a configuration
        # set. If one is found, the configuration set allows notifications
        # regarding the email to be sent to the endpoints set in AWS (i.e.
        # emails, https, etc ...).
        # Depending on the event received (i.e.Bounce, delivery, rejected...),
        # different endpoints can be notified.
        # Without this header, the email is sent but no notification will be
        # sent to the endpoints.
        values_to_pass_to_ses = {
            "send_record class": send_record.__class__.__name__,
            "send_record id": str(send_record.id),
        }
        # The Comments header is a non structured header that allows us to pass
        # arbitrary data to SES. See https://www.ietf.org/rfc/rfc0822.txt
        # for more information.
        # This header field accepts text as value, so we create a string from a
        # dictionary.
        comments_header = json.dumps(values_to_pass_to_ses)
        headers = {
            "X-SES-CONFIGURATION-SET": settings.AWS_CONFIGURATION_SET_NAME,
            "Comments": comments_header}

        email = mail.EmailMultiAlternatives(
            subject=tb_object.subject,
            body=plain_text_message,
            from_email=from_email,
            to=recipient_list,
            headers=headers,
        )
        email.attach_alternative(html_message, "text/html")

        return email

    def _set_email_context(
            self, recipient: list, send_record_id: int,
            tb_object) -> dict:
        """
        Return the context for the email to be sent.

        Keyword arguments:
        recipient -- the list of recipients
        send_record_id -- the id of the send record attached to the email

        Returns:
        A dict containing the context to use to render the email.
        """
        context = dict()
        # If the key k_render_as_email is present in the context, the
        # render must assume we are rendering to email.  More
        # important, it if is absent the render must assume we are
        # rendering to a web page.
        context[k_render_as_email] = True
        context["email"] = tb_object

        # The unsubscribe link is created with the send_record and the
        # user's email hidden in a token.
        context["token"] = \
            self.get_unsubscribe_token(recipient[0], send_record_id)
        context["beacon_token"] = \
            self.get_beacon_token(send_record_id)

        # On May 31th 2022 :
        #
        # While sending a press release, it appears that at least 10 token out
        # of 24 were invalid. We know this because we got 10 times a
        # "token_valid: invalid token" error on GET requests to the
        # 'mailing_list:press_subscription_management' url, seconds after the
        # send.
        # These errors all occured on the same try except block in
        # asso_tn.urls.token_valid(), the one including :
        #
        # "timed_token = urlsafe_base64_decode(encoded_timed_token).decode()"
        #
        # Using the same tokens raises UnicodeError and once a ValueError.
        # Attemps to create and decode tokens from the very same mails and
        # send_record ids didn't raise any errors.
        #
        # In an attempt to reproduce and understand the error, we log more
        # details about it for the next time it appears
        # See issue https://github.com/transport-nantes/tn_web/issues/777
        logger.info(f"Token {context['token']} is associated "
                    f"with Email {recipient[0]} and SR.id {send_record_id}")

        return context

    def create_send_record(self,  slug: str, mailing_list: MailingList,
                           recipient: str):
        """
        Create a new send record object.

        Keyword arguments:
        slug -- the slug of the object to send
        mailing_list -- the mailing list to send a the object to
        recipient -- the recipient's email

        Returns:
        A SendRecord object linking the email and the user.

        """
        recipient_user_object = User.objects.get(email=recipient)
        send_record = self.send_record_class(
            slug=slug,
            mailinglist=mailing_list,
            recipient=recipient_user_object,
        )
        send_record.save()
        logger.info("Created send record " + str(type(send_record)))
        return send_record

    def get_unsubscribe_token(self, email: str, send_record_id: int) -> str:
        """
        Create a token to unsubscribe the user from the mailing list.
        """
        k_minutes_in_six_months = 60*24*30*6
        token = make_timed_token(
            email, k_minutes_in_six_months, int_key=send_record_id)
        return token

    def get_beacon_token(self, send_record_id: int) -> str:
        """Create a new beacon token.

        Create a beacon token that encodes the send_record_class and
        send_record_id for the mail message we are sending.

        Keyword arguments:
        send_record_id -- the id of the send record attached to the email

        Returns:
        A token that can be used to retrieve the send_record_class and
        send_record_id attached to the email.
        """
        send_record_class_string = self.send_record_class.__name__
        k_minutes_in_six_months = 60*24*30*6
        token = make_timed_token(
            send_record_class_string, k_minutes_in_six_months,
            int_key=send_record_id)
        return token


class TopicBlogBaseSendView(FormView, SendableObjectMixin):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # The slug is then used to get the TBEmail we want to send.
        context["tbe_slug"] = self.kwargs['the_slug']
        if not hasattr(self, "base_model"):
            raise ImproperlyConfigured("base_model must be a class with a "
                                       "send_object_url attribute")
        context["send_to_view"] = self.base_model.send_object_url
        context["base_model"] = self.base_model
        context["sent_object"] = self.base_model.objects.filter(
            slug=self.kwargs['the_slug'],
            publication_date__isnull=False
            ).order_by("date_created").last()
        return context

    def form_valid(self, form):
        tbe_slug = self.kwargs['the_slug']
        tbe_object = self.get_last_published_email(tbe_slug)

        if tbe_object is None:
            logger.info(f"No published {self.base_model.send_object_url} "
                        f"object found for '{tbe_slug}'")
            raise Http404(
                f"Pas de '{self.base_model.description_of_object}' publié "
                f"trouvé pour le slug '{tbe_slug}'")

        mailing_list_token = form.cleaned_data['mailing_list']
        # The recipient list is extracted from the selected MailingList.
        mailing_list = MailingList.objects.get(
            mailing_list_token=mailing_list_token)
        mailing_list: MailingList
        recipient_list = get_subcribed_users_email_list(mailing_list)

        # We create and send an email for each recipient, each with
        # custom informations (like the unsubscribe link).
        for recipient in recipient_list:
            try:
                send_record = self.create_send_record(
                    slug=tbe_slug,
                    mailing_list=mailing_list,
                    recipient=recipient)
            except IntegrityError:
                logger.info(f"{recipient} already received an email for "
                            f"{tbe_slug}")
                continue
            custom_email = self.prepare_email(
                pkid=tbe_object.id,
                the_slug=tbe_slug,
                recipient=[recipient],
                mailing_list=mailing_list,
                send_record=send_record)

            logger.info(f"Successfully prepared email to {recipient}")
            try:
                custom_email.send(fail_silently=False)
                send_record.handoff_time = datetime.now(timezone.utc)
                send_record.save()
                logger.info(f"Successfully sent email to {recipient}")
            except Exception as e:
                logger.error(f"Failed to send email to {recipient} : {e}")
                send_record.status = "FAILED"
                send_record.save()

        return super().form_valid(form)


class TopicBlogSelfSendView(PermissionRequiredMixin, LoginRequiredMixin,
                            SendableObjectMixin, BaseFormView):
    """Allow sending TB objects to oneself by email.

    Authorised users can send to themselves sendable objects (eg TBPress and
    TBEmail) by email.
    """
    permission_required = ('topicblog.tbe.may_send', 'topicblog.tbp.may_send')
    form_class = SendToSelfForm
    send_record_class = None

    def form_valid(self, form):
        sent_object_id = form.cleaned_data['sent_object_id']
        sent_object_class = form.cleaned_data['sent_object_class']
        sent_object_transactional_send_record_class_name = form.cleaned_data[
            'sent_object_transactional_send_record_class']
        self.success_url = \
            form.cleaned_data['redirect_url'] + "?email_sent=true"

        logger.info(f"Sending {sent_object_class} {sent_object_id} to "
                    f"{self.request.user.email}")
        self.send_email_to_self(
            sent_object_id, sent_object_class,
            sent_object_transactional_send_record_class_name)
        return super().form_valid(form)

    def send_email_to_self(
            self, sent_object_id: int,
            sent_object_class: str,
            sent_object_transactional_send_record_class_name: str) \
            -> None:
        """Send an email to the user with the given email address."""
        # Retrieve the object to send.
        object_class = apps.get_model('topicblog', sent_object_class)
        object_to_send = object_class.objects.get(id=sent_object_id)

        # Create a send record.
        logger.info("Creating send record...")
        send_record = self.create_send_record(
            object_to_send,
            sent_object_transactional_send_record_class_name)
        if not send_record:
            logger.info("No send record created, aborting the send.")
            return None

        # Prepare the email.
        self.template_name = (
            object_to_send.template_config[object_to_send.template_name]
            .get("email_template")
        )
        context = self._set_email_context(
            recipient=[self.request.user.email],
            send_record_id=send_record.id,
            tb_object=object_to_send
        )
        custom_email = self._create_email_object(
            tb_object=object_to_send,
            context=context,
            recipient_list=[self.request.user.email],
            send_record=send_record,
        )
        # Send the email.
        try:
            custom_email.send(fail_silently=False)
            send_record.handoff_time = datetime.now(timezone.utc)
            send_record.save()
            logger.info(f"Sent email to {self.request.user.email}")
        except Exception as e:
            logger.error(
                f"Failed to send email to {self.request.user.email} : {e}")
            send_record.status = "FAILED"
            send_record.save()

    def create_send_record(
        self,
        object_to_send: Union[TopicBlogEmail, TopicBlogPress],
        sent_object_transactional_send_record_class_name: str) \
            -> Union[Type[SendRecordTransactional], None]:
        """Return the proper send record for the given class.

        Keyword argument:
        object_to_send -- the object we are sending, a sendable Topicblog item
        sent_object_transactional_send_record_class_name -- the class name of
            the send record we want to create.

        Returns:
        The send record for the given object.
        Or if an error prevents the creation of a send record, None.
        """
        # Get the send record class.
        try:
            self.send_record_class = apps.get_model(
                "topicblog",
                sent_object_transactional_send_record_class_name)
        except LookupError:
            logger.info(f"{sent_object_transactional_send_record_class_name}"
                        " does not exist in topicblog.models")
            return None

        # Fill the send record object
        kwargs = {
            "recipient": self.request.user,
            "slug": getattr(
                object_to_send, "slug",
                f"{object_to_send.__class__.__name__}-{object_to_send.id}"),
        }
        send_record = self.send_record_class(**kwargs)
        send_record.save()

        logger.info(
            f"Created send record : Recipient: {self.request.user.email}, "
            f"send record: {self.send_record_class} - "
            f"{send_record.id}")

        return send_record

######################################################################
# TopicBlogItem


@StaffRequired
def get_slug_dict(request):
    """Return a list of all existing slugs"""
    model_name = request.GET.get('model_name', None)
    if not model_name:
        return JsonResponse({"error": "model_name is required"})
    model = apps.get_model('topicblog', model_name)
    qs = model.objects.order_by('slug').values('slug')
    dict_of_slugs = Counter([item['slug'] for item in qs])
    return JsonResponse(dict_of_slugs, safe=False)


@StaffRequired
def get_url_list(request):
    """Return an url directing to a list of items
    given a slug.
    """
    slug = request.GET.get('slug')
    url = reverse("topicblog:list_items_by_slug", args=[slug])
    return JsonResponse({'url': url})


class TopicBlogItemEdit(PermissionRequiredMixin, TopicBlogBaseEdit):
    """
    Create or modify a TBItem.

    """
    model = TopicBlogItem
    form_class = TopicBlogItemForm
    permission_required = 'topicblog.tbi.may_edit'

    def form_post_process(self, tb_item, tb_existing, form):
        """
        Perform any post-processing of the form.
        Following args are defined in TopicBlogEditBase.form_valid()

            tb_item : Item created from the form's POST

            tb_existing : Item retrieved from the database if we are
            editing an existing item. None otherwise.

            form : form from request.POST
        """

        # If we are editing an existing item, the ImageField values
        # won't be copied over -- they aren't included in the rendered
        # form.  Checking the "clear" box in the form will still clear
        # the image fields if needed.
        #
        # This is largely because we're using FormView instead of
        # CreateView / UpdateView.
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            tb_existing: TopicBlogItem
            image_fields = tb_existing.get_image_fields()
            for field in image_fields:
                if field in form.cleaned_data and \
                        form.cleaned_data[field] is None:
                    setattr(tb_item, field, getattr(tb_existing, field))

        # template field being set in the ModelForm it needs to be specifically
        # set here before saving.
        tb_item.template_name = form.cleaned_data["template_name"]

        return tb_item


class TopicBlogItemView(TopicBlogBaseView):
    """
    Render a TopicBlogItem.

    """
    model = TopicBlogItem


class TopicBlogItemViewOnePermissions(PermissionRequiredMixin):
    """Custom Permission class to require different permissions
    depending on whether the user is requesting a GET or a POST.

    Default behaviour is at class level and doesn't allow a
    per-method precision.
    """

    def has_permission(self) -> bool:
        user = self.request.user
        if self.request.method == 'POST':
            return user.has_perm('topicblog.tbi.may_publish')
        elif self.request.method == 'GET':
            return user.has_perm('topicblog.tbi.may_view')
        return super().has_permission()


class TopicBlogItemViewOne(TopicBlogItemViewOnePermissions,
                           TopicBlogBaseViewOne):
    model = TopicBlogItem


class TopicBlogItemList(PermissionRequiredMixin, TopicBlogBaseList):
    model = TopicBlogItem
    permission_required = 'topicblog.tbi.may_view'


######################################################################
# TopicBlogEmail

class TopicBlogEmailViewOnePermissions(PermissionRequiredMixin):
    """Custom Permission class to require different permissions
    depending on whether the user is requesting a GET or a POST.

    Default behaviour is at class level and doesn't allow a
    per-method precision.
    """

    def has_permission(self) -> bool:
        user = self.request.user
        if self.request.method == 'POST':
            return user.has_perm('topicblog.tbe.may_publish')
        elif self.request.method == 'GET':
            return user.has_perm('topicblog.tbe.may_view')
        return super().has_permission()


class TopicBlogEmailEdit(PermissionRequiredMixin,
                         TopicBlogBaseEdit):
    model = TopicBlogEmail
    permission_required = 'topicblog.tbe.may_edit'
    form_class = TopicBlogEmailForm

    def form_post_process(self, tb_email, tb_existing, form):
        """
        Perform any post-processing of the form.
        Following args are defined in TopicBlogEditBase.form_valid()
            tb_email: topicblog email object created from the form's POST
            tb_existing: topicblog email object retrieved from the
            database if we are editing an existing object. None otherwise.
            form: form from request.POST
        """

        # If we are editing an existing topicblog email object, the
        # ImageField values won't be copied over -- they aren't
        # included in the rendered form.  Checking the "clear" box
        # in the form will still clear the image fields if needed.
        #
        # This is largely because we're using FormView instead of
        # CreateView / UpdateView.
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            tb_existing: TopicBlogEmail
            image_fields = tb_existing.get_image_fields()
            for field in image_fields:
                if field in form.cleaned_data and \
                        form.cleaned_data[field] is None:
                    setattr(tb_email, field, getattr(tb_existing, field))
        return tb_email


class TopicBlogEmailView(TopicBlogBaseView):
    model = TopicBlogEmail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb_object = context['page']
        user = self.request.user
        if user.has_perm('topicblog.tbe.may_send_self') or \
           (user.has_perm('topicblog.tbe.may_send') and
                tb_object.publisher != user):
            context['sendable'] = True
        return context


class TopicBlogEmailViewOne(TopicBlogEmailViewOnePermissions,
                            TopicBlogBaseViewOne):
    model = TopicBlogEmail
    transactional_send_record_class = SendRecordTransactionalEmail


class TopicBlogEmailList(PermissionRequiredMixin, TopicBlogBaseList):
    model = TopicBlogEmail
    permission_required = 'topicblog.tbe.may_view'


class TopicBlogEmailSend(PermissionRequiredMixin, LoginRequiredMixin,
                         TopicBlogBaseSendView):
    """ Allow TopicBlogEmails to be sent and tracked through emails. """
    permission_required = 'topicblog.tbe.may_send'
    form_class = TopicBlogEmailSendForm
    template_name = 'topicblog/topicblogbase_send_form.html'
    send_record_class = SendRecordMarketingEmail
    base_model = TopicBlogEmail
    # For now, successfully sending an email will redirect to the
    # homepage. We'll probably want to redirect to the email
    # itself eventually, or on the dashboard ?
    success_url = "/"


@perm_required("topicblog.tbe.may_send")
def get_number_of_recipients(request, *args, **kwargs):
    """
    Return the number of recipients for a given mailing list.
    """
    mailing_list_token = kwargs.get("mailing_list_token", None)
    if not mailing_list_token:
        return HttpResponseBadRequest()
    mailing_list = get_object_or_404(MailingList,
                                     mailing_list_token=mailing_list_token)
    number_of_recipients = user_subscribe_count(mailing_list)
    return JsonResponse({"count": number_of_recipients})


######################################################################
# TopicBlogPress


class TopicBlogPressViewOnePermissions(PermissionRequiredMixin):
    """Custom Permission class to require different permissions
    depending on whether the user is requesting a GET or a POST.

    Default behaviour is at class level and doesn't allow a
    per-method precision.
    """

    def has_permission(self) -> bool:
        user = self.request.user
        if self.request.method == 'POST':
            return user.has_perm('topicblog.tbp.may_publish')
        elif self.request.method == 'GET':
            return user.has_perm('topicblog.tbp.may_view')
        return super().has_permission()


class TopicBlogPressEdit(PermissionRequiredMixin,
                         TopicBlogBaseEdit):
    model = TopicBlogPress
    permission_required = 'topicblog.tbp.may_edit'
    form_class = TopicBlogPressForm

    def form_post_process(self, tb_press, tb_existing, form):
        """
        Perform any post-processing of the form.
        Following args are defined in TopicBlogEditBase.form_valid()
            tb_press : topicblog press object created from the form's POST
            tb_existing : topicblog press object retrieved from the
            database if we are editing an existing object. None otherwise.
            form : form from request.POST
        """

        # If we are editing an existing topicblog email object, the
        # ImageField values won't be copied over -- they aren't
        # included in the rendered form.  Checking the "clear" box
        # in the form will still clear the image fields if needed.
        #
        # This is largely because we're using FormView instead of
        # CreateView / UpdateView.
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            tb_existing: TopicBlogLauncher
            image_fields = tb_existing.get_image_fields()
            for field in image_fields:
                if field in form.cleaned_data and \
                        form.cleaned_data[field] is None:
                    setattr(tb_press, field, getattr(tb_existing, field))
        return tb_press


class TopicBlogPressView(TopicBlogBaseView):
    model = TopicBlogPress

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tb_object = context['page']
        user = self.request.user
        if user.has_perm('topicblog.tbp.may_send_self') or \
           (user.has_perm('topicblog.tbp.may_send') and
                tb_object.publisher != user):
            context['sendable'] = True
        return context


class TopicBlogPressViewOne(TopicBlogPressViewOnePermissions,
                            TopicBlogBaseViewOne):
    model = TopicBlogPress
    transactional_send_record_class = SendRecordTransactionalPress


class TopicBlogPressList(PermissionRequiredMixin,
                         TopicBlogBaseList):
    """List available press releases."""

    model = TopicBlogPress
    permission_required = 'topicblog.tbp.may_view'


class TopicBlogPressSend(PermissionRequiredMixin, LoginRequiredMixin,
                         TopicBlogBaseSendView):
    """Email a TBPress."""

    permission_required = 'topicblog.tbp.may_send'
    form_class = TopicBlogEmailSendForm
    template_name = 'topicblog/topicblogbase_send_form.html'
    send_record_class = SendRecordMarketingPress
    base_model = TopicBlogPress
    # For now, successfully sending an email will redirect to the
    # homepage. We'll probably want to redirect to the email
    # itself eventually, or on the dashboard ?
    success_url = "/"


######################################################################
# TopicBlogLauncher

class TopicBlogLauncherViewOnePermissions(PermissionRequiredMixin):
    """Custom Permission class to require different permissions
    depending on whether the user is requesting a GET or a POST.

    Default behaviour is at class level and doesn't allow a
    per-method precision.
    """

    def has_permission(self) -> bool:
        user = self.request.user
        if self.request.method == 'POST':
            return user.has_perm('topicblog.tbla.may_publish')
        elif self.request.method == 'GET':
            return user.has_perm('topicblog.tbla.may_view')
        return super().has_permission()


class TopicBlogLauncherEdit(PermissionRequiredMixin,
                            TopicBlogBaseEdit):
    model = TopicBlogLauncher
    permission_required = 'topicblog.tbla.may_edit'
    form_class = TopicBlogLauncherForm

    def form_post_process(self, tb_launcher, tb_existing, form):
        """
        Perform any post-processing of the form.
        Following args are defined in TopicBlogEditBase.form_valid()
            tb_launcher: topicblog launcher object created from the form's POST
            tb_existing: topicblog launcher object retrieved from the
            database if we are editing an existing object. None otherwise.
            form: form from request.POST
        """

        # If we are editing an existing topicblog email object, the
        # ImageField values won't be copied over -- they aren't
        # included in the rendered form.  Checking the "clear" box
        # in the form will still clear the image fields if needed.
        #
        # This is largely because we're using FormView instead of
        # CreateView / UpdateView.
        pkid = self.kwargs.get('pkid', -1)
        if pkid > 0:
            tb_existing: TopicBlogLauncher
            image_fields = tb_existing.get_image_fields()
            for field in image_fields:
                if field in form.cleaned_data and \
                        form.cleaned_data[field] is None:
                    setattr(tb_launcher, field, getattr(tb_existing, field))
        return tb_launcher


class TopicBlogLauncherView(TopicBlogBaseView):
    """This view is a bit curious.  In real life, TBLauncher's will be
    inserted into pages via a templatetag.  But for the purpose of
    editing and viewing them, we need a single page that displays
    them.  That is this page.

    """
    model = TopicBlogLauncher


class TopicBlogLauncherViewOne(TopicBlogLauncherViewOnePermissions,
                               TopicBlogBaseViewOne):
    """View a TBLauncher by pk id."""

    model = TopicBlogLauncher


class TopicBlogLauncherList(PermissionRequiredMixin, TopicBlogBaseList):
    """View a list of TBLaunchers."""

    model = TopicBlogLauncher
    permission_required = 'topicblog.tbla.may_view'


######################################################################
# TopicBlogMailingListPitch


class TopicBlogMailingListPitchView(TopicBlogBaseView):
    """View a published mailing list pitch."""

    model = TopicBlogMailingListPitch


class TopicBlogMailingListPitchEdit(PermissionRequiredMixin,
                                    TopicBlogBaseEdit):
    """Edit a TBMailingList Pitch."""

    model = TopicBlogMailingListPitch
    permission_required = 'topicblog.tbmlp.may_edit'
    form_class = TopicBlogMailingListPitchForm


class TopicBlogMailingListPitchList(PermissionRequiredMixin,
                                    TopicBlogBaseList):
    """List available TBMailingListPitches."""

    model = TopicBlogMailingListPitch
    permission_required = 'topicblog.tbmlp.may_view'


class TopicBlogMailingListPitchViewOnePermissions(PermissionRequiredMixin):
    """Custom Permission class to require different permissions
    depending on whether the user is requesting a GET or a POST.

    Default behaviour is at class level and doesn't allow a
    per-method precision.
    """

    def has_permission(self) -> bool:
        user = self.request.user
        if self.request.method == 'POST':
            return user.has_perm('topicblog.mlp.may_publish')
        elif self.request.method == 'GET':
            return user.has_perm('topicblog.mlp.may_view')
        return super().has_permission()


class TopicBlogMailingListPitchViewOne(
        TopicBlogMailingListPitchViewOnePermissions,
        TopicBlogBaseViewOne):
    """View a TBMailingListPitch by pk id."""

    model = TopicBlogMailingListPitch


######################################################################
# TopicBlogWrapper


class TopicBlogWrapperEdit(PermissionRequiredMixin, TopicBlogBaseEdit):
    """Create a TBWrapper."""

    model = TopicBlogWrapper
    permission_required = 'topicblog.tbw.may_edit'
    form_class = TopicBlogWrapperForm


class TopicBlogWrapperView(TemplateView):
    """Display a TBWrapper's underlying content.

    Because TBWrappers do not have their own content, this view
    simply displays the content of the underlying TB object.
    """

    model = None

    def set_model(self, tb_wrapper: TopicBlogWrapper) -> None:
        """Set self.model to the wrapped object original model class

        e.g. TopicBlogItem, TopicBlogPress, TopicBlogEmail, etc.
        """

        self.model: Type['TopicBlogObjectBase'] = \
            apps.get_model("topicblog", tb_wrapper.original_model)

    def override_social_context(
            self, tb_wrapper: TopicBlogWrapper, context: dict) -> dict:
        """Override the social context for the wrapped object."""
        social = {}
        social['twitter_title'] = tb_wrapper.twitter_title
        social['twitter_description'] = tb_wrapper.twitter_description
        social['twitter_image'] = tb_wrapper.twitter_image

        social['og_title'] = tb_wrapper.og_title
        social['og_description'] = tb_wrapper.og_description
        social['og_image'] = tb_wrapper.og_image

        context['social'] = social

        return context

    def get_wrapped_object_viewbyslug_view_class(
            self, tb_wrapper: TopicBlogWrapper) -> Type['View']:
        """Return the the wrapped object's viewbyslug view class

        The wrapped object has a custom get_context_data method in the
        view that usually displays it, for example TopicBlogItems are displayed
        by TopicBlogItemView, which defines a get_context_data method.

        We return the class that displays the wrapped object so we can use
        appropriate functions to set context.
        """
        if not self.model:
            self.set_model(tb_wrapper)

        # Get the path that usually displays the wrapped object by slug
        wrapped_object_viewbyslug_url = (
            reverse(self.model.viewbyslug_object_url,
                    kwargs={"the_slug": tb_wrapper.underlying_slug})
        )

        # Resolve the path to a view class, e.g. TopicBlogItemView if the
        # wrapped object is a TopicBlogItem
        wrapped_object_viewbyslug_view = (
            resolve(wrapped_object_viewbyslug_url).func.view_class
        )

        return wrapped_object_viewbyslug_view

    def instantiate_view_class(
            self, view_class: Type['View'], tb_wrapper: TopicBlogWrapper) -> 'View':
        """Instantiate a view class with the request and kwargs

        We need to instantiate the view class so we can use its
        get_context_data method to set context.
        """
        view = view_class()
        view.request = self.request
        view.kwargs: dict = self.kwargs
        # By default, the "the_slug" kwarg comes from URL, but we don't
        # want to use the wrapper's slug, we want to use the underlying
        # object's slug
        view.kwargs.update({"the_slug": tb_wrapper.underlying_slug})
        return view

    def get_context_data(self, **kwargs):
        tb_wrapper: TopicBlogWrapper = get_object_or_404(
            TopicBlogWrapper,
            slug=self.kwargs["the_slug"],
        )
        self.set_model(tb_wrapper)
        # Get the view class that usually displays the wrapped object
        viewbyslug_view_class = (
            self.get_wrapped_object_viewbyslug_view_class(tb_wrapper)
        )

        # Instantiate the wrapped object's view class so we can use its
        # get_context_data
        view = self.instantiate_view_class(viewbyslug_view_class, tb_wrapper)
        # Depending on the view, we fetch kwargs either in self.kwargs or
        # in **kwargs. So we update both to not use the URL slug, but the
        # underlying slug to make the queries in both cases.
        context = viewbyslug_view_class.get_context_data(
            view, the_slug=tb_wrapper.underlying_slug)
        # The template name is defined in the wrapped object's view class
        self.template_name = view.template_name
        context = self.override_social_context(tb_wrapper, context)
        return context


def beacon_view(response, **kwargs):
    """Process received mail beacon."""
    def update_send_record_open_time(token: str) -> None:
        """Update the token's associated send record's open time.

        Keyword argument :
        token -- The beacon token embedded in the email the user received.

        Returns:
        None
        """
        send_record_class_string, send_record_id = token_valid(token)
        if not send_record_id:
            logger.info(
                    f"The token {token} provided an incorrect "
                    f"ID : {send_record_id} "
                    f"(Class string : {send_record_class_string}")
            return None

        try:
            send_record_class = \
                apps.get_model("topicblog", send_record_class_string)
            # In case the token is valid, we update the open_time
            send_record = send_record_class.objects.get(pk=send_record_id)
            if not send_record.open_time:
                send_record.open_time = datetime.now(timezone.utc)
                send_record.save()
                logger.info(
                    f"{send_record.recipient.email} opened email"
                    f" ({send_record_class_string} SR.id :{send_record.pk})")
        except ObjectDoesNotExist:
            logger.info(f"No send record with id {send_record_id} in class"
                        f" {send_record_class_string}.")
            return None
        except LookupError:
            logger.info(
                f"No send record class with name {send_record_class_string}.")
            return None

    def make_beacon_response() -> FileResponse:
        """Make a response that contains the beacon image."""
        path_to_beacon = (Path(__file__).parent.parent / "asso_tn" / "static" /
                          "asso_tn" / "beacon.gif")
        image = open(path_to_beacon, "rb")
        response = FileResponse(image, content_type="image/gif")
        return response

    # We remove the ".gif" from the end of the token
    token = kwargs['token'][:-4]
    update_send_record_open_time(token)
    response = make_beacon_response()
    return response


def _extract_data_from_ses_signal(mail_obj: dict) -> Tuple[str, str, str]:
    """Extract data attached to a mail object received on SES-webhook.

    Keyword Argument:
    - mail_obj : A dict containing data related to a sent email

    Return:
    - A tuple containing :
        - The AWS message ID
        - The "send_record class" attached in the "Comments" header
        - The "send_record id" attached in the "Comments" header
    """
    aws_message_id = mail_obj.get("messageId")
    send_record_class = None
    send_record_id = None
    headers_content = mail_obj.get("headers")
    comments_header = next(
        (header for header in headers_content
         if header["name"] == "Comments"), None)
    if comments_header:
        try:
            comments_values: dict = json.loads(comments_header["value"])
            send_record_class = comments_values.get("send_record class")
            send_record_class = apps.get_model('topicblog', send_record_class)
            send_record_id = comments_values.get("send_record id")
            send_record_id = int(send_record_id)
        except Exception as e:
            logger.error(
                f"Error extracting data from comments header : {e}")
            send_record_class = None
            send_record_id = None

    return aws_message_id, send_record_class, send_record_id


@receiver(send_received)
def send_received_handler(sender, mail_obj, send_obj, *args, **kwargs):
    """Handle AWS SES send_received notifications.

    AWS Receiver
    This function will run when a send_received is received from
    Amazon SES.
    The signal is sent from django_ses' view.
    """
    logger.info("Received send_received.")
    aws_message_id, send_record_class, send_record_id = \
        _extract_data_from_ses_signal(mail_obj)
    logger.info(f"Received send_received for {aws_message_id}")
    logger.info(f"  {send_record_class} ID : {send_record_id}")
    if send_record_class and send_record_id:
        try:
            send_record = send_record_class.objects.get(pk=send_record_id)
            send_record.status = "SENT"
            send_record.send_time = datetime.now(timezone.utc)
            send_record.aws_message_id = aws_message_id
            send_record.save()
            logger.info(f"send_received : {send_record_class.__name__} id={send_record.pk}")
        except Exception as e:
            logger.error(
                f"Error while updating send_record : {e}")


@receiver(open_received)
def open_received_handler(sender, mail_obj, open_obj, *args, **kwargs):
    """Handle AWS SES open_received notifications

    AWS Receiver
    This function will run when a open_received is received from
    Amazon SES.
    The signal is sent from django_ses' view.

    We voluntarily ignore open_received notifications because
    we already have the beacon view handling that for us.

    We mean to disable this feature in AWS console, but we handle them so we
    know if we receive them.
    """
    logger.info("open_received received !")
    aws_message_id, send_record_class, send_record_id = \
        _extract_data_from_ses_signal(mail_obj)
    logger.info(
        f"\nopen_received signal received for message {aws_message_id}\n"
        f"SendRecord class : {send_record_class} ID : {send_record_id}")


@receiver(click_received)
def click_received_handler(sender, mail_obj, click_obj, *args, **kwargs):
    """Handle AWS SES click_received notifications

    AWS Receiver
    This function will run when a click_received is received from
    Amazon SES.
    The signal is sent from django_ses' view.

    We voluntarily ignore click_received notifications because
    the click redirection from amazon is flagged in uBlock as tracker.
    We don't want our clicks to scare any user.

    We mean to disable this feature in AWS console, but we handle them so we
    know if we receive them.
    """
    logger.info("click_received received !")
    aws_message_id, send_record_class, send_record_id = \
        _extract_data_from_ses_signal(mail_obj)
    logger.info(
        f"\nclick_received signal received for message {aws_message_id}\n"
        f"SendRecord class : {send_record_class} ID : {send_record_id}")


def mark_moribund_and_delete(slug_queryset):
    """Delete or prepare to delete old objects.

    Mark for deletion objects that are moribund.
    Delete objects that have been marked moribund for long enough.

    I really don't like that the queryset language doesn't permit me
    to use a function, as this means that the functions defined on the
    model (which can only apply to individual instances) can't be used
    here, and the queryset definitions of moribund and deletable can't
    be used there, even if I made a new manager.

    Somewhat worse, I don't see how to do the SQL queries efficiently
    in django's query language in order to call update().  So, rather
    inefficiently, I'm loading all unpublished objects for the slug.
    In principle, that isn't too inefficient, since after a few weeks
    there likely won't be any.

    """
    slug_queryset.filter(publication_date=None)
    for tb_object in slug_queryset:
        if tb_object.is_deletable():
            logger.info(f"Deleting object {tb_object.id}.")
            tb_object.delete()
        elif tb_object.is_moribund() and \
                tb_object.scheduled_for_deletion_date is None:
            logger.info(f"Marking as moribund object {tb_object.id}.")
            tb_object.scheduled_for_deletion_date = datetime.now(timezone.utc)
            tb_object.save()
