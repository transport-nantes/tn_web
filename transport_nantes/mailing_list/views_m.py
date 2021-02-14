from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.crypto import get_random_string
from .models import MailingList, MailingListEvent, Petition

from .views import MailingListSignup, QuickMailingListSignup, MailingListMerci
from .forms import QuickPetitionSignupForm
from asso_tn.views import AssoView

from django.views.generic.edit import FormView

class MailingListSignupM(MailingListSignup):
    template_name = 'mailing_list/signup_m.html'
    merci_template = 'mailing_list/merci_m.html'

class QuickMailingListSignupM(QuickMailingListSignup):
    template_name = 'mailing_list/quick_signup_m.html'
    merci_template = 'mailing_list/merci_m.html'

class MailingListMerciM(MailingListMerci):
    template_name = 'mailing_list/merci_m.html'

class QuickPetitionSignup(FormView):
    template_name = 'mailing_list/quick_signup_m.html'
    merci_template = 'mailing_list/merci_petition.html' # This needs to be parameterised by petition.
    form_class = QuickPetitionSignupForm

    # We don't currently populate this form with the user's current
    # subscriptions.  If the user is logged in, we should.  This then
    # becomes the edit form as well.

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = 'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg'
        context['hero_title'] = 'Newsletter'
        print('----------get context data--------')
        return context

    def form_valid(self, form):
        """Process a valid QuickPetitionSignup.

        This method is called when valid form data has been POSTed.
        It returns an HttpResponse.
        """
        subscribe = False
        user = User.objects.filter(email=form.cleaned_data['email']).first()
        if user is None:
            user = User()   # New user.
            user.username = get_random_string(20)
            user.first_name = form.cleaned_data['first_name'] or 'firstname'
            user.last_name = form.cleaned_data['last_name'] or 'lastname'
            user.email = form.cleaned_data['email']
            user.save()
        print('----------3')
        # user.profile.commune = form.cleaned_data['commune']
        # user.profile.code_postal = form.cleaned_data['code_postal']
        # user.profile.save()
        
        print('----------4')
        petition = MailingList.objects.filter(
            mailing_list_token=form.cleaned_data['petition_name'])
        if len(petition) == 0:
            return HttpResponseNotFound("Pétition inconnu")
        subscription = MailingListEvent.objects.create(
            user=user,
            mailing_list=petition[0],
            event_type=MailingListEvent.EventType.SUBSCRIBE)
        subscription.save()
        print('----------5')
        return render(
            self.request, self.merci_template,
            {
                'hero': True,
                'hero_image':
                'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg',
                'hero_title': 'Newsletter',
            }
        )

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
        return context
