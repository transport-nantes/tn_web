from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render
# from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string
from .forms import ClickCollectForm
from .models import ClickableCollectable, ClickAndCollect

# Create your views here.

class GiletReserveView(FormView):
    template_name = 'clickcollect/reserve.html'
    form_class = ClickCollectForm
    # success_url = reverse_lazy('click_collect:gilet_reserved')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = 'velopolitain/gilet-banner.png'
        context['hero_title'] = 'Les rencontres visibles'
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        #form.send_email()
        user = form.save(commit=False)
        try:
            user.refresh_from_db()
        except ObjectDoesNotExist:
            print('ObjectDoesNotExist')
            pass            # I'm not sure this can ever happen.
        if user is None or user.pk is None:
            user = User.objects.filter(email=form.cleaned_data['email']).first()
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
        gilet = ClickableCollectable.objects.get(collectable_token='gilet-transport-nantes')
        click_and_collect = ClickAndCollect.objects.create(user=user, collectable=gilet)
        click_and_collect.save()
        # return super(GiletReserveView, self).form_valid(form)
        return render(self.request, 'clickcollect/reserved.html',
                      {
                          'hero': True,
                          'hero_image': 'velopolitain/gilet-banner.png',
                          'hero_title': 'Les rencontres visibles',
                      }
        )

class GiletReservedView(TemplateView):
    """View class only used whilst debugging.

    This is useful for revealing the thank you page, but under normal
    circumstances it should not be revealed without first filling out
    the form.

    """
    template_name = 'clickcollect/reserved.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero'] = True
        context['hero_image'] = 'velopolitain/gilet-banner.png'
        context['hero_title'] = 'Les rencontres visibles'
        context['hero_description'] = '(actuellement debugging)'
        return context
