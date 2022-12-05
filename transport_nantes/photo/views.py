"""Application to manage a photo competition."""
import logging
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import (HttpRequest, HttpResponse,
                         HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, CreateView, FormView, ListView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist

from asso_tn.utils import make_timed_token, token_valid
from .forms import (PhotoEntryForm, AnonymousVoteForm,
                    SimpleVoteForm, SimpleVoteFormWithConsent)
from .models import PhotoEntry, Vote
from .events import get_user_vote
from mailing_list.models import MailingList
from mailing_list.events import subscribe_user_to_list

logger = logging.getLogger("django")


class ForbiddenException(Exception):
    """Exception to raise if the user is not allowed to vote"""
    pass


class UploadEntry(LoginRequiredMixin, CreateView):
    """
    Form to collect Photo entries
    """
    model = PhotoEntry
    form_class = PhotoEntryForm

    success_url = reverse_lazy('photo:confirmation')

    def get(self, request, *args, **kwargs):
        logger.info(f"UploadEntry.get() from {request.user}")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Override the post method to add the user to the form
        """
        form = self.get_form()
        self.object = None
        form.instance.user = request.user
        if form.is_valid():
            try:
                logger.info("Received photo submission.")
                mailing_list = MailingList.objects.get(
                    mailing_list_token="operation-pieton")
                user = request.user
                subscribe_user_to_list(user, mailing_list)
                logger.info(f"Subscribed user {user} to list {mailing_list}.")
            except ObjectDoesNotExist:
                logger.error("Mailing list operation-pieton does not exist")

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Override the form_valid method to add the user's submission to session
        """
        self.object = form.save()
        encoded_object_id = make_timed_token(
            string_key="", int_key=self.object.id, minutes=60*24*30)
        self.success_url += f"?submission={encoded_object_id}"
        return HttpResponseRedirect(self.get_success_url())


class Confirmation(TemplateView):
    """
    Confirmation page after successful submit of a PhotoEntry
    """
    template_name = 'photo/confirmation.html'

    def get(self, request, *args, **kwargs):
        logger.info(f"Confirmation.get() from {request.user}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_submitted_photo = None
        submission_token = self.request.GET.get("submission")
        string_key, photo_id = token_valid(submission_token)

        if photo_id and string_key == "":
            last_submitted_photo = \
                PhotoEntry.objects.get(id=photo_id)
        if last_submitted_photo:
            context["submitted_photo"] = \
                last_submitted_photo.submitted_photo.url

        return context


class PhotoView(FormView):
    """
    View to display a single photo and up/down vote it
    """
    template_name = 'photo/single_entry.html'
    form_class = AnonymousVoteForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Overriding here so we can return HttpResponseForbidden if needed"""
        try:
            context_or_response = self.get_context_data()
        except ForbiddenException as exception:
            return HttpResponseForbidden(exception)
        return self.render_to_response(context_or_response)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo_sha1 = self.kwargs.get("photo_sha1")
        photo = get_object_or_404(PhotoEntry, sha1_name=photo_sha1)
        tn_session_id = self.request.session.get("tn_session")
        user = self.request.user if self.request.user.is_authenticated else None

        if not photo.accepted:
            # Author and authorized users can see the photo
            if not any([
                self.request.user == photo.user,
                self.request.user.has_perm('photo.may_see_unaccepted_photos')
            ]):
                raise ForbiddenException(
                    "Cette photo n'as pas encore été acceptée")
        context["photo"] = photo

        if photo.accepted:
            self.set_next_and_previous_arrows(context, photo)
            # Because it's possible that user is not authenticated (anonymous vote)
            # we need to check if the user has already voted for this photo
            # using its session id as well.
            if Vote.objects.filter(
                    # user here could be null hence the
                    # need to check if user is authenticated
                    Q(user=user) if user else Q()
                    | Q(tn_session_id=tn_session_id),
                    captcha_succeeded=True,
            ).exists():
                context["has_voted"] = True
            else:
                context["has_voted"] = False

            # To set the proper styles on the vote buttons, we check if the
            # user has already voted on this photo
            last_vote = get_user_vote(
                self.request.user, photo, tn_session_id=tn_session_id)

            if last_vote:
                if last_vote.vote_value is True:
                    context["last_vote"] = "upvote"
                elif last_vote.vote_value is False:
                    context["last_vote"] = "downvote"

            if not last_vote and user:
                # If user is logged in but never voted, we ask for consent
                # to send them emails
                context["form"] = SimpleVoteFormWithConsent()

            context["social"] = {
                "og_title": "Les mobilitains organisent l'opération piéton",
                "og_description": "Votez pour vos clichés préférés !",
                "og_image": photo.submitted_photo.url,
                "twitter_image": photo.submitted_photo.url,
                "twitter_creator": "@mobilitain",
                "twitter_site": "mobilitains.fr",
            }

        return context

    def set_next_and_previous_arrows(self, context: dict, photo: 'PhotoEntry') -> None:
        """
        Set the next and previous photo arrows

        context is passed by reference.
        """
        all_accepted_photos = list(PhotoEntry.objects.filter(accepted=True))
        current_photo_index = all_accepted_photos.index(photo)
        if current_photo_index > 0:
            context["previous_photo"] = all_accepted_photos[
                current_photo_index - 1]
        if current_photo_index < len(all_accepted_photos) - 1:
            context["next_photo"] = all_accepted_photos[
                current_photo_index + 1]

    def get_initial(self):
        """Set the initial value in the form"""
        initial = super().get_initial()
        initial["photoentry_sha1_name"] = self.kwargs.get("photo_sha1")
        return initial

    def post(self, request, *args, **kwargs):
        """
        Instantiate the proper form instance with the passed POST variables.

        This method is overriden because the default form is AnonymousVoteForm,
        but this can be overridden under certain conditions : If the user is
        logged in and / or has already voted on any photo.

        Overriding will allow the self.get_form() method to return a different
        form and thus form.is_valid() will be performed against the proper form.
        """
        user = request.user if request.user.is_authenticated else None
        tn_session_id = request.session.get("tn_session")
        # If there is a vote with the same user or if the user has already
        # voted with this session, we no longer user the AnonymousVoteForm
        # for simplicity
        if Vote.objects.filter(
                Q(user=user)
                | Q(tn_session_id=tn_session_id),
                captcha_succeeded=True).exists():
            self.form_class = SimpleVoteForm

        # If the user is logged in but never voted, we use the form with
        # consent
        elif not Vote.objects.filter(user=user).exists() and user:
            self.form_class = SimpleVoteFormWithConsent

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle the forms submissions

        This view can have 3 different forms, all targeted to create a vote
        event and optionally subscribe user to a mailing list.

        The 3 forms are:
        - AnonymousVoteForm: Used when the user is not logged in and has not
        voted yet. The form is used to create a vote and subscribe the user
        to the mailing list if they agree to it.
        - SimpleVoteForm: Used when the user is logged in or has already
        voted with this session. User was already asked for consent at this
        point and it's not asked again.
        - SimpleVoteFormWithConsent: Used when the user is logged in but
        never voted. The form is used to create a vote and subscribe the user
        to the mailing list if they agree to it. The difference is that this
        form doesn't ask for email or captcha compared to AnonymousVoteForm.

        """
        # The photo sha1 is included in the URL
        photo_sha1 = self.kwargs.get("photo_sha1")
        photo = get_object_or_404(PhotoEntry, sha1_name=photo_sha1)
        if not photo.accepted:
            return HttpResponseForbidden("Photo not accepted")

        if not self.request.user.is_authenticated:
            # email address is only asked in anonymous vote form
            email_address = self.request.POST.get("email_address", None)
            if email_address:
                user = User.objects.get_or_create(email=email_address)[0]
            else:
                # When the user is anon and has already voted previously,
                # we don't ask for email address
                user = None
        else:
            user = self.request.user

        # Consent is asked in both anonymous and logged in vote forms
        # only while the user hasn't voted yet. Consent box is opt-in :
        # if the user doesn't check it, we subscribe them to the mailing
        # list.
        no_consent = self.request.POST.get("consent_box", None)
        if not no_consent and user and self.form_class != SimpleVoteForm:
            try:
                mailing_list = MailingList.objects.get(
                    mailing_list_token="operation-pieton")
                subscribe_user_to_list(user, mailing_list)
                logger.info(
                    f"Subscribed user {user.email} to list {mailing_list}.")
            except MailingList.DoesNotExist:
                logger.error(
                    "Mailing list operation-pieton does not exist")

        # vote value is a constant among the forms
        vote_value = self.request.POST.get("vote_value", None)
        if vote_value == "upvote":
            vote_value = True
        elif vote_value == "downvote":
            vote_value = False
        else:
            return HttpResponseForbidden("Invalid vote")

        # Always set at page load
        tn_session_id = self.request.session.get('tn_session', None)

        Vote.objects.create(
            user=user,
            tn_session_id=tn_session_id,
            photo_entry=photo,
            vote_value=vote_value,
            captcha_succeeded=True,
        )

        # The Ajax request will execute the success function upon receiving
        # a 200 response
        return HttpResponse(status=200)

    def form_invalid(self, form):
        """Handle invalid forms

        We keep the failed attempts because we want to gather contacts of
        people who might be open to having conversations with us,
        supporting us.
        """
        # The photo sha1 is included in the URL
        photo_sha1 = self.kwargs.get("photo_sha1")
        photo = get_object_or_404(PhotoEntry, sha1_name=photo_sha1)
        if not photo.accepted:
            return HttpResponseForbidden("Photo not accepted")

        if not self.request.user.is_authenticated:
            # email address is only asked in anonymous vote form
            email_address = self.request.POST.get("email_address", None)
            if email_address:
                user = User.objects.get_or_create(email=email_address)[0]
            else:
                # When the user is anon and has already voted previously,
                # we don't ask for email address
                user = None
        else:
            user = self.request.user

        # Consent is asked in both anonymous and logged in vote forms
        # only while the user hasn't voted yet. Consent box is opt-in :
        # if the user doesn't check it, we subscribe them to the mailing
        # list.
        no_consent = self.request.POST.get("consent_box", None)
        if not no_consent and user:
            try:
                mailing_list = MailingList.objects.get(
                    mailing_list_token="operation-pieton")
                subscribe_user_to_list(user, mailing_list)
                logger.info(
                    f"Subscribed user {user.email} to list {mailing_list}.")
            except MailingList.DoesNotExist:
                logger.error(
                    "Mailing list operation-pieton does not exist")

        # vote value is a constant among the forms
        vote_value = self.request.POST.get("vote_value", None)
        if vote_value == "upvote":
            vote_value = True
        elif vote_value == "downvote":
            vote_value = False
        else:
            return HttpResponseForbidden("Invalid vote")

        # Always set at page load
        tn_session_id = self.request.session.get('tn_session', None)

        Vote.objects.create(
            user=user,
            tn_session_id=tn_session_id,
            photo_entry=photo,
            vote_value=vote_value,
            # The captcha field is the only one that can have failed at this
            # point
            captcha_succeeded=False,
        )

        return HttpResponse(status=200)


class PhotoListView(ListView):
    queryset = PhotoEntry.objects.filter(accepted=True)
    allow_empty = True
    paginate_by = 4
