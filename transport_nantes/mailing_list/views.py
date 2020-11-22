from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from django.urls import reverse_lazy
from .forms import MailingListSignupForm
from .models import MailingList, MailingListEvent

# Create your views here.

class MailingListSignup(FormView):
    template_name = 'mailing_list/signup.html'
    form_class = MailingListSignupForm
    # success_url = reverse_lazy('mailing_list:list_ok')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('MailingListSignup')
        context['hero'] = True
        context['hero_image'] = 'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg'
        context['hero_title'] = 'Newsletter'
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        #form.send_email()
        subscribe = False
        print("Form is valid")
        user = form.save(commit=False)
        print((user, user.pk, user.email))
        try:
            user.refresh_from_db()
        except ObjectDoesNotExist:
            print('ObjectDoesNotExist')
            print((user, user.id, user.pk,))
            pass            # I'm not sure this can ever happen.
        print((user, user.pk,))
        if user is None or user.pk is None:
            user = User.objects.filter(email=form.cleaned_data['email']).first()
            if user is None:
                user = User()   # New user.
                user.username = get_random_string(20)
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.email = form.cleaned_data['email']
        user.profile.commune = form.cleaned_data['commune']
        user.profile.code_postal = form.cleaned_data['code_postal']
        user.save()
        user.profile.save()
        print(user, user.profile)
        if form.cleaned_data['monthly']:
            newsletter = MailingList.objects.get(
                mailing_list_token='general-monthly')
            subscription = MailingListEvent.objects.create(
                user=user,
                mailing_list=newsletter,
                event_type=MailingListEvent.EventType.SUBSCRIBE)
            subscription.save()
            subscribe = True
            print(subscription)
        if form.cleaned_data['quarterly']:
            newsletter = MailingList.objects.get(
                mailing_list_token='general-quarterly')
            subscription = MailingListEvent.objects.create(
                user=user,
                mailing_list=newsletter,
                event_type=MailingListEvent.EventType.SUBSCRIBE)
            subscription.save()
            subscribe = True
            print(subscription)
        if subscribe:
            return render(
                self.request, 'mailing_list/merci.html',
                {
                    'hero': True,
                    'hero_image':
                    'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg',
                    'hero_title': 'Newsletter',
                }
            )
        return super(MailingListSignup, self).form_valid(form)

class MailingListMerci(TemplateView):
    template_name = 'mailing_list/merci.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = 'asso_tn/images-libres/black-and-white-bridge-children-194009-1000.jpg'
        context['hero_title'] = 'Newsletter'
        return context

