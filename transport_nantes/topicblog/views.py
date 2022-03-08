from collections import Counter
from datetime import datetime, timezone
import logging
from django.conf import settings
from django.core import mail

from django.db.models import Count, Max
from django.http import Http404, HttpResponseServerError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags

from asso_tn.utils import StaffRequired, make_timed_token
from mailing_list.events import get_subcribed_users_email_list
from mailing_list.models import MailingList
from .models import (TopicBlogItem, TopicBlogEmail, TopicBlogPress,
                     TopicBlogLauncher)
from .forms import TopicBlogItemForm, TopicBlogEmailSendForm

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

    def get_context_data(self, **kwargs):
        # In FormView, we must use the self.kwargs to retrieve the URL
        # parameters. This stems from the View class that transfers
        # the URL parameters to the View instance and assigns kwargs
        # to self.kwargs.
        pk_id = self.kwargs.get('pkid', -1)
        slug = self.kwargs.get('the_slug', '')

        if pk_id > 0:
            tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)
            kwargs["form"] = self.form_class(instance=tb_object)
            context = super().get_context_data(**kwargs)
        else:
            tb_object = self.model()
            context = super().get_context_data(**kwargs)
        context['tb_object'] = tb_object
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
            ).order_by("date_modified").last()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk_id = kwargs.get('pkid', -1)
        slug = kwargs.get('the_slug', '')
        tb_object = get_object_or_404(self.model, id=pk_id, slug=slug)

        # We set the template in the model.
        self.template_name = tb_object.template_name
        context['page'] = tb_object
        tb_object: self.model  # Type hint for linter
        context = tb_object.set_social_context(context)
        context['topicblog_admin'] = True
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
                self.model.objects.filter(
                    slug=tb_object.slug).exclude(
                        id=tb_object.id).update(publication_date=None)
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
        context = super().get_context_data(**kwargs)
        qs = context['object_list']
        the_slug = self.kwargs.get('the_slug', None)
        if the_slug:
            context['slug'] = the_slug
            context['servable_object'] = qs.filter(
                publication_date__lte=datetime.now(timezone.utc)).order_by(
                    '-publication_date').first()
        return context

    def get_queryset(self, *args, **kwargs):
        """Return a queryset of matches for a given the_slug.
        """
        qs = super(ListView, self).get_queryset(*args, **kwargs)
        if 'the_slug' in self.kwargs:
            the_slug = self.kwargs['the_slug']
            return qs.filter(slug=the_slug).order_by(
                '-date_modified')
        return qs.values('slug') \
                 .annotate(count=Count('slug'),
                           date_modified=Max('date_modified'),
                           publication_date=Max('publication_date')) \
                 .order_by('-date_modified')


######################################################################
# TopicBlogItem


@StaffRequired
def get_slug_suggestions(request):
    """Return a JSON list of suggested slugs.

    This is a helper function for the AJAX call to get the list of
    suggested slugs.  It is called from the template.

    """
    partial_slug = request.GET.get('partial_slug')
    slug_list = TopicBlogItem.objects.filter(
        slug__contains=partial_slug).order_by("-id")[:20]
    slug_list = slug_list.values_list('slug', flat=True)
    # Why did we use set instead of applying DISTINCT() ?
    # Because Django doesn't support DISTINCT(*field) on
    # databases other than Postgres. We tried to use raw queries
    # but it proved to be unsuccessful.
    slug_list = set(slug_list)
    return JsonResponse(list(slug_list), safe=False)


@StaffRequired
def get_slug_dict(request):
    """Return a list of all existing slugs"""
    qs = TopicBlogItem.objects.order_by('slug').values('slug')
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
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm

    permission_required = 'topicblog.tbi.may_edit'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        tb_item = context['tb_object']

        context["form_admin"] = ["slug", "template", "title", "header_image",
                                 "header_title", "header_description",
                                 "header_slug", "content_type"]
        context["form_content_a"] = ["body_text_1_md", "cta_1_slug",
                                     "cta_1_label", "body_text_2_md",
                                     "cta_2_slug", "cta_2_label", ]
        context["form_content_b"] = ["body_image", "body_image_alt_text",
                                     "body_text_3_md", "cta_3_slug",
                                     "cta_3_label", ]
        context["form_social"] = ["social_description", "twitter_title",
                                  "twitter_description", "twitter_image",
                                  "og_title", "og_description", "og_image"]
        context["form_notes"] = ["author_notes"]

        context["slug_fields"] = tb_item.get_slug_fields()

        return context

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
        tb_item.template_name = form.cleaned_data["template"]

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

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicblogitem_list_one.html'] + names
        else:
            return names


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
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm


class TopicBlogEmailView(TopicBlogBaseView):
    model = TopicBlogEmail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_appropriate_base_template'] = \
            'topicblog/base_email.html'
        tb_object = context['page']
        user = self.request.user
        if user.has_perm('topicblog.tbe.may_send_self') or \
           (user.has_perm('topicblog.tbe.may_send')
                and tb_object.publisher != user):
            context['sendable'] = True
        return context


class TopicBlogEmailViewOne(TopicBlogEmailViewOnePermissions,
                            TopicBlogBaseViewOne):
    model = TopicBlogEmail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_appropriate_base_template'] = \
            'topicblog/base_email.html'
        return context


class TopicBlogEmailList(PermissionRequiredMixin, TopicBlogBaseList):
    model = TopicBlogEmail
    permission_required = 'topicblog.tbe.may_view'

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicblogemail_list_one.html'] + names
        else:
            return names


class TopicBlogEmailSend(PermissionRequiredMixin, LoginRequiredMixin,
                         FormView):
    """Notes to Benjamin and Mickael:

    This view isn't implemented yet.  Here's what I think you should do:

    1.  On GET, display a form.  That form should (for now) just show
    the mailing_lists available in a dropdown list and let the user
    choose one.  Once a mailing_list is chosen, enable a send button.
    Pushing the send button will POST to the same url.

    2.  On POST, send the mail.  This means you do the following:
        (i)  Get the list of users from the mailing_list by calling
             subscribed_users() from mailing_list/events.py.  Note that
             that function doesn't exist yet, but it should be a really,
             really simple function for you to write based on the other
             functions in the file.  You should make a single commit
             with that function and tests for that function.
        (ii) For each user in the list:

             Compute a timed_token (function already exists,
             make_timed_token() in asso_tn/utils.py).  Given it a
             three-week timeout so as not to over-think.  Pass the
             TopicBlogEmailSendRecord pk_id in persistent.  If someone
             comes back after expiration, we can ask them to respond
             to a new query (not for today).  In the footer of the
             base email template (note: this is 30 seconds, you just
             write "<div><div><p><a href={% url
             ... %}>unsubscribe</a></div></div>" with maybe some
             arguments to the divs and such.  DO NOT spend time now
             fiddling with making it look just right.  There's a
             difference between unworldly user interaction paradigms
             and simply not being pretty yet.  The latter is easily
             remedied in a second commit, the former is trickier.
             This is a commit.

             Also compute the url (the path already exists) to view
             this email on the web.  Put that in the context, too, and
             make sure you add a link at the top of the email base
             template, just above the content.  That's another commit.

             Render the email, pass it off to SES for sending, and
             write a record to TopicBlogEmailSendRecord.  This is
             another commit.

             Now write a function that serves a beacon.  A beacon
             means you have a non-threatening path (NOT
             /tb/e/beacon/<value>/ but rather /tb/e/i/<value>/ -- and
             value is going to be another timed_token that encodes the
             pk_id of the TopicBlogEmailSendRecord) that returns a
             one-pixel background-colour gif.  We can change it later,
             that will work for now.  This is a commit.

             Now go back to the above and add a beacon to the email
             base template.  Give it a ten year time-out, which is
             nine years and six months more than we probably need.
             That means you generate the beacon value and pass it in
             so that the image (/tb/e/i/<value>) has the right value.
             This is a commit.

             Note that the two timed tokens encode the email address
             to which we sent the mail and the pk_id of the
             TopicBlogEmailSendRecord, so the beacon function or the
             unsub page can easily look up the send record.  The
             beacon function should update
             TopicBlogEmailSendRecord.open_time.  Clicks should lead
             to setting TopicBlogEmailSendRecord.click_time.  In both
             cases, only if not already set, since what we want is the
             time of the first view, the first click.  This is a
             commit.

             If the user validates an unsub having clicked in from an
             email, then we have the timed token handy and we should
             set TopicBlogEmailSendRecord.unsubscribe_time if it's not
             already set (and call unsubscribe_user_from_list()).

    """
    permission_required = 'topicblog.tbe.may_send'
    form_class = TopicBlogEmailSendForm
    template_name = 'topicblog/topicblogemail_send_form.html'
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tbe_slug"] = self.kwargs['the_slug']
        return context

    def get_last_published_email(self, tbe_slug: str) -> TopicBlogEmail:
        """Gets the TBEmail object with the most recent publication date
        for a given slug."""
        tbe_object = TopicBlogEmail.objects.filter(
            slug=tbe_slug,
            publication_date__isnull=False
            ).order_by('-publication_date').first()
        return tbe_object

    def form_valid(self, form):
        tbe_slug = self.kwargs['the_slug']
        tbe_object = self.get_last_published_email(tbe_slug)

        if tbe_object is None:
            logger.info(f"No published TBEmail object found for '{tbe_slug}'")
            raise Http404(
                f"Pas d'email publié trouvé pour le slug '{tbe_slug}'")

        mailing_list_token = form.cleaned_data['mailing_list']
        # The recipient list is extracted from a MailingList.
        mailing_list = MailingList.objects.get(
            mailing_list_token=mailing_list_token)
        mailing_list: MailingList
        recipient_list = get_subcribed_users_email_list(mailing_list)

        for recipient in recipient_list:
            custom_email = self.prepare_email(
                pkid=tbe_object.id,
                the_slug=tbe_slug,
                recipient=[recipient],
                mailing_list=mailing_list,)

            logger.info(f"Successfully prepared email to {recipient}")
            custom_email.send(fail_silently=False)

        return super().form_valid(form)

    def prepare_email(self, pkid: int, the_slug: str, recipient: list,
                      mailing_list: MailingList) \
            -> mail.EmailMultiAlternatives:
        """
        Creates a sendable email object from a TBEmail with a mail
        client-friendly template, given a pkid, a slug and a mail adress.
        """
        if pkid < 0 or the_slug is None:
            logger.info(f"pkid < 0 ({pkid}) or slug is none ({the_slug})")
            return HttpResponseServerError()

        # Preparing the email
        tb_email = TopicBlogEmail.objects.get(pk=pkid, slug=the_slug)
        self.template_name = tb_email.template_name
        context = dict()
        context["context_appropriate_base_template"] = \
            "topicblog/base_email.html"
        context["email"] = tb_email

        try:
            email = self._create_email_object(tb_email, context, recipient)
        except Exception as e:
            logger.info(
                f"Error while creating EmailMultiAlternatives object: {e}")
            raise Exception(
                f"Error while creating EmailMultiAlternatives object: {e}")

        return email

    def _create_email_object(self, tb_email: TopicBlogEmail, context: dict,
                             recipient_list: list,
                             from_email: str = settings.DEFAULT_FROM_EMAIL) \
            -> mail.EmailMultiAlternatives:
        """
        To send emails to multiple persons, django send_mail function isn't
        enough, we need to create a EmailMultiAlternatives object to be able,
        for example to put recipients in BCC field or add attachments.
        It also improves the performances by reusing the same connexion to SMTP
        server.
        Doc :
        https://docs.djangoproject.com/en/3.2/topics/email/#sending-multiple-emails
        https://docs.djangoproject.com/en/3.2/topics/email/#emailmessage-objects
        https://docs.djangoproject.com/en/3.2/topics/email/#sending-alternative-content-types
        """
        # HTML message is the one displayed in mail client
        html_message = render_to_string(
            tb_email.template_name, context=context)
        # In cases where the HTML message isn't accepted, a plain text
        # message is displayed in the mail client.
        plain_text_message = strip_tags(html_message)

        email = mail.EmailMultiAlternatives(
            subject=tb_email.subject,
            body=plain_text_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_message, "text/html")

        return email

    def _set_email_context(self, recipient: list, mailing_list: MailingList,
                           slug: str) -> dict:
        """
        Sets the context for the email to be sent.
        """
        context = dict()
        context["context_appropriate_base_template"] = \
            "topicblog/base_email.html"
        # TODO: create a unsub link
        args = (recipient, slug, mailing_list)  # TODO: Add missing args
        # The make_timed_token function isn't ready yet (8/3/22)
        context["unsub_link"] = make_timed_token(*args)

        # TODO: Create a template tag to have redirect links embedded in the
        # email.

        return context


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
    template_name = 'topicblog/tb_item_edit.html'
    form_class = TopicBlogItemForm


class TopicBlogPressView(TopicBlogBaseView):
    model = TopicBlogPress

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_appropriate_base_template'] = \
            'topicblog/base_press.html'
        tb_object = context['page']
        user = self.request.user
        if user.has_perm('topicblog.tbp.may_send_self') or \
           (user.has_perm('topicblog.tbp.may_send')
                and tb_object.publisher != user):
            context['sendable'] = True
        return context


class TopicBlogPressViewOne(TopicBlogPressViewOnePermissions,
                            TopicBlogBaseViewOne):
    model = TopicBlogPress

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_appropriate_base_template'] = \
            'topicblog/base_press.html'
        return context


class TopicBlogPressList(PermissionRequiredMixin,
                         TopicBlogBaseList):
    model = TopicBlogPress
    permission_required = 'topicblog.tbp.may_view'

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicblogpress_list_one.html'] + names
        else:
            return names


class TopicBlogPressSend(PermissionRequiredMixin, LoginRequiredMixin,
                         TemplateView):
    """Notes to Benjamin and Mickael:

    This view isn't implemented yet.  Here's what I think you should do:

    1.  On GET, display a form.  That form should (for now) just show
    the mailing_lists available in a dropdown list and let the user
    choose one.  Once a mailing_list is chosen, enable a send button.
    Pushing the send button will POST to the same url.

    Soon-ish, we should add a "press" flag to mailing lists, but
    that's not today.  Our goal today is got move.  Just, in the back
    of your head, think that we'll eventually filter on a press flag.

    2.  On POST, send the mail.  This means you do the following:
        (i)  Get the list of users from the mailing_list by calling
             subscribed_users() from mailing_list/events.py.  Note that
             that function doesn't exist yet, but it should be a really,
             really simple function for you to write based on the other
             functions in the file.  You should make a single commit
             with that function and tests for that function.
        (ii) For each user in the list:

             Compute a timed_token (function already exists,
             make_timed_token() in asso_tn/utils.py).  Given it a
             three-week timeout so as not to over-think.  Pass the
             TopicBlogPressSendRecord pk_id in persistent.  If someone
             comes back after expiration, we can ask them to respond
             to a new query (not for today).  In the footer of the
             base press template (note: this is 30 seconds, you just
             write "<div><div><p><a href={% url
             ... %}>unsubscribe</a></div></div>" with maybe some
             arguments to the divs and such.  DO NOT spend time now
             fiddling with making it look just right.  There's a
             difference between unworldly user interaction paradigms
             and simply not being pretty yet.  The latter is easily
             remedied in a second commit, the former is trickier.
             This is a commit.

             Also compute the url (the path already exists) to view
             this press on the web.  Put that in the context, too, and
             make sure you add a link at the top of the press base
             template, just above the content.  That's another commit.

             Render the press, pass it off to SES for sending, and
             write a record to TopicBlogPressSendRecord.  This is
             another commit.

             Now write a function that serves a beacon.  A beacon
             means you have a non-threatening path (NOT
             /tb/e/beacon/<value>/ but rather /tb/e/i/<value>/ -- and
             value is going to be another timed_token that encodes the
             pk_id of the TopicBlogPressSendRecord) that returns a
             one-pixel background-colour gif.  We can change it later,
             that will work for now.  This is a commit.

             Now go back to the above and add a beacon to the press
             base template.  Give it a ten year time-out, which is
             nine years and six months more than we probably need.
             That means you generate the beacon value and pass it in
             so that the image (/tb/e/i/<value>) has the right value.
             This is a commit.

             Note that the two timed tokens encode the press address
             to which we sent the mail and the pk_id of the
             TopicBlogPressSendRecord, so the beacon function or the
             unsub page can easily look up the send record.  The
             beacon function should update
             TopicBlogPressSendRecord.open_time.  Clicks should lead
             to setting TopicBlogPressSendRecord.click_time.  In both
             cases, only if not already set, since what we want is the
             time of the first view, the first click.  This is a
             commit.

             If the user validates an unsub having clicked in from an
             press, then we have the timed token handy and we should
             set TopicBlogPressSendRecord.unsubscribe_time if it's not
             already set (and call unsubscribe_user_from_list()).

             Hints for the future: once this is working, we're going
             to improve it with things like our logo in the mail, the
             date and other press release type things.  Also, the
             unsub button will have some special press-like features,
             like letting journalists specify the specific lists to
             which they want to be subscribed.  Maybe you care about
             pedestrians but not about inter-city buses, and maybe we
             some day have lists for those.

    """
    permission_required = 'topicblog.tbp.may_send'
    pass


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
    template_name = 'topicblog/tb_launcher_edit.html'
    form_class = TopicBlogItemForm


class TopicBlogLauncherView(TopicBlogBaseView):
    """This view is a bit curious.  In real life, TBLauncher's will be
    inserted into pages via a templatetag.  But for the purpose of
    editing and viewing them, we need a single page that displays
    them.  That is this page.

    """
    model = TopicBlogLauncher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_appropriate_base_template'] = \
            'topicblog/base_launcher.html'
        return context


class TopicBlogLauncherViewOne(TopicBlogLauncherViewOnePermissions,
                               TopicBlogBaseViewOne):
    model = TopicBlogLauncher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TopicBlogLauncherList(PermissionRequiredMixin, TopicBlogBaseList):
    model = TopicBlogLauncher
    permission_required = 'topicblog.tbla.may_view'

    def get_template_names(self):
        names = super().get_template_names()
        if 'the_slug' in self.kwargs:
            return ['topicblog/topicbloglauncher_list_one.html'] + names
        else:
            return names
