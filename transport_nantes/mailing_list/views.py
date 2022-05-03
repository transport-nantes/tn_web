import logging
from datetime import datetime, timezone

from asso_tn.utils import token_valid
from asso_tn.views import AssoView
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Case, When, Subquery, OuterRef
from django.db.models.expressions import Value
from django.http import (Http404, HttpResponseBadRequest, HttpResponseNotFound,
                         HttpResponseServerError)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import FormView, ListView, TemplateView
from topicblog.models import TopicBlogEmailSendRecord

from .events import (subscribe_user_to_list, subscriber_count,
                     unsubscribe_user_from_list, user_current_state,
                     user_subscribe_count)
from .forms import (FirstStepQuickMailingListSignupForm, MailingListSignupForm,
                    QuickMailingListSignupForm, QuickPetitionSignupForm,
                    SubscribeUpdateForm)
from .models import MailingList, Petition, MailingListEvent

logger = logging.getLogger("django")


class MailingListSignup(FormView):
    template_name = 'mailing_list/signup_m.html'
    merci_template = 'mailing_list/merci_m.html'
    form_class = MailingListSignupForm
    # success_url = reverse_lazy('mailing_list:list_ok')

    # We don't currently populate this form with the user's current
    # subscriptions.  If the user is logged in, we should.  This then
    # becomes the edit form as well.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = ('asso_tn/images-libres/'
                                 'black-and-white-bridge-children-194009-1000'
                                 '.jpg')
        context['hero_title'] = 'Newsletter'
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # form.send_email()
        subscribe = False
        user = form.save(commit=False)
        try:
            user.refresh_from_db()
        except ObjectDoesNotExist:
            logger.error('ObjectDoesNotExist')
            pass            # I'm not sure this can ever happen.
        if user is None or user.pk is None:
            user = User.objects.filter(
                email=form.cleaned_data['email']).first()
            if user is None:
                user = User()   # New user.
                user.username = get_random_string(20)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
        user.save()
        user.profile.commune = form.cleaned_data['commune']
        user.profile.code_postal = form.cleaned_data['code_postal']
        user.profile.save()
        for newsletter in form.cleaned_data['newsletters']:
            subscribe_user_to_list(user, newsletter)
            # At some point we should also store the last known
            # subscription state in a table with foreign key user.  If
            # the user is in that table, we use it, otherwise we look
            # up in mailing_list_events.  (We'll always need this
            # extra lookup, because a newly created list won't
            # populate users' current (unsubscribed) state.
            #
            # We should wait until this is a performance issue, however.
            subscribe = True
        if subscribe:
            template_name = "mailing_list/merci_m.html"
            return render(self.request, template_name, {'user': user})
        return super(MailingListSignup, self).form_valid(form)


class QuickMailingListSignup(FormView):
    template_name = 'mailing_list/quick_signup_m.html'
    form_class = FirstStepQuickMailingListSignupForm

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            user = self.request.user
            email = form.cleaned_data.get('email', user.email)
        else:
            user = None
            email = form.cleaned_data['email']
        mailinglist = form.cleaned_data['mailinglist']
        captcha = form.cleaned_data.get('captcha', None)
        if captcha is None and not self.request.user.is_authenticated:
            # No captcha and don't know the user, so ask for proof of
            # humanity.
            next_form = QuickMailingListSignupForm()
            next_form["email"].initial = email
            next_form["mailinglist"].initial = mailinglist
            return render(self.request, self.template_name,
                          {"form": next_form})

        self.template_name = "mailing_list/merci_m.html"
        # Maybe we don't know the user.
        if not user:
            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                user = User()
                user.username = get_random_string(20)
                user.email = email
                logger.info(f"Created new user with email {user.email}")
                user.save()
        # If we can't find the mailinglist, that's our bug.
        try:
            mailing_list_obj = MailingList.objects.get(
                mailing_list_token=mailinglist)
        except ObjectDoesNotExist:
            logger.info(
                f"Failed to find mailing_list_token={mailinglist}")
            return HttpResponseServerError()
        subscribe_user_to_list(user, mailing_list_obj)

        if mailing_list_obj.linked_article:
            kwargs = {
                "the_slug": mailing_list_obj.linked_article.slug,
                }
            url = (reverse_lazy("topicblog:view_item_by_slug", kwargs=kwargs)
                   + '?just_subscribed=true')
            return redirect(to=url)
        return render(self.request, self.template_name, {})

    def form_invalid(self, form):
        """Display the correct form.
        This is actually a bit of a hack.  We should build the correct
        form, extract the email address from the incoming form, and
        then display the correct thing.  I think.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            email = form.cleaned_data.get('email', user.email)
        else:
            email = self.request.POST['email']
        mailinglist = self.request.POST['mailinglist']
        next_form = QuickMailingListSignupForm()
        next_form["email"].initial = email
        next_form["mailinglist"].initial = mailinglist
        return render(self.request, self.template_name, {'form': next_form})

    def get(self, request, *args, **kwargs):
        form = FirstStepQuickMailingListSignupForm()
        self.kwargs['mailinglist'] = request.GET.get('mailinglist')
        if self.kwargs['mailinglist']:
            form["mailinglist"].initial = self.kwargs['mailinglist']
        else:
            return redirect(f"{reverse_lazy('index')}#newsletter")
        return render(self.request, self.template_name, {"form": form})

    def get_form_class(self, *args, **kwargs):
        post_data = dict(self.request.POST)
        is_captcha_form = post_data.get("captcha_0", None)
        if is_captcha_form:
            return QuickMailingListSignupForm
        else:
            return FirstStepQuickMailingListSignupForm


class QuickPetitionSignup(FormView):
    template_name = 'mailing_list/quick_signup_m.html'
    # This needs to be parameterised by petition.
    merci_template = 'mailing_list/merci_petition.html'
    form_class = QuickPetitionSignupForm
    success_url = reverse_lazy('mailing_list:list_ok')
    # We don't currently populate this form with the user's current
    # subscriptions.  If the user is logged in, we should.  This then
    # becomes the edit form as well.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = ('asso_tn/images-libres/'
                                 'black-and-white-bridge-children-194009-1000'
                                 '.jpg')
        context['hero_title'] = 'Newsletter'
        return context

    def form_valid(self, form):
        """Process a valid QuickPetitionSignup.

        This method is called when valid form data has been POSTed.
        It returns an HttpResponse.
        """
        user = User.objects.filter(email=form.cleaned_data['email']).first()
        if user is None:
            user = User()   # New user.
            user.username = get_random_string(20)
            user.first_name = form.cleaned_data['first_name'] or 'firstname'
            user.last_name = form.cleaned_data['last_name'] or 'lastname'
            user.email = form.cleaned_data['email']
            user.save()
        # user.profile.commune = form.cleaned_data['commune']
        # user.profile.code_postal = form.cleaned_data['code_postal']
        # user.profile.save()

        petition = MailingList.objects.filter(
            mailing_list_token=form.cleaned_data['petition_name'])
        if len(petition) == 0:
            return HttpResponseNotFound("Pétition inconnu")
        subscribe_user_to_list(user, petition[0])
        return render(self.request, self.merci_template, {})


class PetitionView(AssoView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Need to look up petition here.
        # Fetch Markdown for entire petition.
        # Add to context.
        petition = get_object_or_404(Petition, slug=kwargs['petition_slug'])
        petition.set_context(context)
        context['body_text_1'] = petition.petition1_md
        context['body_text_2'] = petition.petition2_md
        context['body_text_3'] = petition.petition3_md
        context['body_text_4'] = petition.petition4_md
        context['petition'] = petition
        context['petition_token'] = petition.mailing_list.mailing_list_token
        # context['hero_image'] = 'asso_tn/traffic-1600.jpg'
        context['page'] = {'hero_image': 'asso_tn/traffic-1600.jpg',
                           'hero_title': "C'est l'heure de changer"}
        return context


class MailingListListView(LoginRequiredMixin,
                          PermissionRequiredMixin, ListView):
    permission_required = 'mailing_list.view_mailinglist'
    model = MailingList
    template_name = "mailing_list/mailing_list_list_view.html"
    queryset = MailingList.objects.all()
    oder_by = ['is_petition', 'mailing_list_name']
    context_object_name = 'mailing_lists_base'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lists = self.get_queryset()
        context['mailing_lists'] = [(list, user_subscribe_count(list))
                                    for list in lists if not list.is_petition]
        context['petitions_lists'] = [(list, subscriber_count(list))
                                      for list in lists if list.is_petition]
        return context


class UserStatusView(LoginRequiredMixin, ListView):
    model = MailingList
    template_name = "mailing_list/mailing_list_user_status.html"
    context_object_name = 'mailing_lists'
    paginate_by = 10

    def get_queryset(self):
        """Create a list with all active mailing list
        with the current state of the user"""
        object_list = MailingList.objects.filter(
            list_active=True, is_petition=False).order_by(
            'mailing_list_name')
        user = self.request.user
        object_list_with_state = \
            [(mailing_list, user_current_state(user, mailing_list).event_type,)
             for mailing_list in object_list]
        return object_list_with_state

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        """Create a list that contain the current page
           the current page number with 4 numbers if
           this is possible before and after the current
           number."""
        context["number_pagination_list"] = \
            context["paginator"].get_elided_page_range(
            number=context["page_obj"].number,
            on_each_side=4, on_ends=0)
        return context


class MailingListToggleSubscription(LoginRequiredMixin, FormView):
    template_name = 'mailing_list/validate_form.html'
    form_class = SubscribeUpdateForm
    success_url = reverse_lazy('mailing_list:user_status')

    def get(self, request):
        # redirect if the get request don't have a mailinglist
        if not self.request.GET.get("mailinglist"):
            return redirect(reverse_lazy("mailing_list:user_status"))
        return super().get(request)

    def form_valid(self, form):
        mailing_list_id = form.cleaned_data['mailinglist']
        user = self.request.user
        mailing_list = get_object_or_404(MailingList, id=mailing_list_id)
        current_state = user_current_state(user, mailing_list)
        # check the current state and toggle the result
        if current_state.event_type == "unsub":
            subscribe_user_to_list(user, mailing_list)
        else:
            unsubscribe_user_from_list(user, mailing_list)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("mailinglist"):
            mailing_list_id = self.request.GET.get("mailinglist")
            context["mailing_list"] = get_object_or_404(
                MailingList, id=mailing_list_id)
        return context


class NewsletterUnsubscriptionView(TemplateView):

    """
    View to unsubscribe a user from a Newsletter mailing list.
    """
    template_name = "mailing_list/unsubscribe_from_mailing_list.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        token = context['token']
        email, send_record_id = token_valid(token)

        if email is None or send_record_id is None:
            logger.info(f"Token {token} is invalid")
            raise Http404("Désolé, il semblerait qu'il y ait eu une erreur, "
                          "veuillez vérifier que le lien est correct "
                          "s'il vous plaît")

        try:
            send_record = TopicBlogEmailSendRecord.objects.get(
                pk=send_record_id)
        except ObjectDoesNotExist:
            logger.info(f"Send record ID : {send_record_id} not found")
            raise Http404("Désolé, nous n'avons pas retrouvé le contenu "
                          "demandé, vérifiez que votre lien est correct "
                          "s'il vous plaît.")
        context["send_record_mailing_list"] = \
            send_record.mailinglist.mailing_list_name
        context["user_email"] = email

        return context

    def get(self, request, *args, **kwargs):
        try:
            context = self.get_context_data(**kwargs)
        except Http404:
            return HttpResponseNotFound(
                "Ce lien a perdu sa magie en cours de route, nous ne "
                "comprenons plus ce qu'il veut dire ... Il est peut-être "
                "trop vieux, ou invalide.")
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """
        Post method to unsubscribe the user from the mailing list.
        """
        token = kwargs.get("token", None)
        if not token:
            return HttpResponseBadRequest()
        try:
            email, send_record_id = token_valid(token)
        except ValueError:
            logger.info(f"Token {token} is invalid")
            raise Http404()
        send_record = TopicBlogEmailSendRecord.objects.get(pk=send_record_id)
        send_record: TopicBlogEmailSendRecord
        now = datetime.now(timezone.utc)
        unsubscribe_user_from_list(
            send_record.recipient, send_record.mailinglist)
        if send_record.click_time is None:
            send_record.click_time = now
        if send_record.unsubscribe_time is None:
            send_record.unsubscribe_time = now

        send_record.save()
        context = dict(
            confirmed_unsub=True,
            send_record_mailing_list=send_record.mailinglist.mailing_list_name
        )
        logger.info(f"{email} unsubscribed from {send_record.mailinglist}")
        return render(request, self.template_name, context=context)


class PressSubscriptionManagementView(TemplateView):
    """Allows management of Press subscriptions
    Displays the current subscriptions to the different press Mailing lists
    and allows the user to sub / unsub from a checkbox form.

    Press mailing list are those whose attribute mailing_list_type is "PR"
    """
    template_name = "mailing_list/press_subscription_management.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        email, send_record_id = token_valid(kwargs["token"])
        if email and send_record_id:
            context["user"] = User.objects.get(email=email)
            # Adds a .is_subbed property to the mailing lists
            # This evaluates to true if the given user is subbed to
            # the mailing list
            context["press_subscription_list"] = \
                MailingList.objects.filter(
                    mailing_list_type="PRESS"
                    ).order_by("-id"
                    ).annotate(  # noqa
                        is_subbed=Subquery(
                            MailingListEvent.objects
                            .filter(mailing_list=OuterRef('id'),
                                    user=context["user"])
                            .order_by('-event_timestamp')
                            .annotate(is_subbed=Case(
                                When(
                                    event_type=MailingListEvent.EventType.SUBSCRIBE,  # noqa
                                    then=Value(True)),
                                default=Value(False))
                            ).values('is_subbed')[:1])
                    )
        else:
            context["press_subscription_list"] = \
                MailingList.objects.filter(
                    mailing_list_type="PRESS").order_by("-id")

        context["token"] = kwargs["token"]
        return context

    def post(self, request, *args, **kwargs):
        """
        Post method to update the user's press preferences
        """
        token = kwargs.get("token", None)
        if not token:
            return HttpResponseBadRequest()
        try:
            _, send_record_id = token_valid(token)
        except ValueError:
            logger.info(f"Token {token} is invalid")
            raise Http404()
        send_record = TopicBlogEmailSendRecord.objects.get(pk=send_record_id)
        send_record: TopicBlogEmailSendRecord

        # Retrieve from POST the list of mailing lists the user wants to
        # subscribe to
        data = dict(request.POST)
        ml_id_to_subscribe_to = []
        for key, _ in data.items():
            if key.startswith("MAILING_LIST_ID_ITEM_TAG__"):
                ml_id_to_subscribe_to.append(data[key][0])

        press_ml_list_to_sub = MailingList.objects.filter(
            mailing_list_type="PRESS", id__in=ml_id_to_subscribe_to)
        press_ml_list_to_unsub = MailingList.objects.filter(
            mailing_list_type="PRESS").exclude(id__in=ml_id_to_subscribe_to)

        # Subscribes the user to the checked mailing lists
        for ml in press_ml_list_to_sub:
            subscribe_user_to_list(send_record.recipient, ml)

        # Unsubscribes the user from the unchecked mailing lists
        for ml in press_ml_list_to_unsub:
            unsubscribe_user_from_list(send_record.recipient, ml)

        return redirect(reverse_lazy(
            "mailing_list:press_subscription_management",
            kwargs={"token": token}) + "?confirmed_sub=true")
