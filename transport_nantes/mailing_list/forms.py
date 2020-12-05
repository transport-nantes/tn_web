from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from captcha.fields import CaptchaField
from authentication.models import Profile
from .models import MailingList

class MailingListMMCF(forms.ModelMultipleChoiceField):
    """A custom form that gives us pretty mailing list labels in
    MailingListSignupForm.  Without this, we'd get whatever __str__()
    produces, which is not user-friendly.

    Kudos to:
    https://medium.com/swlh/django-forms-for-many-to-many-fields-d977dec4b024

    """

    def label_from_instance(self, member):
        return '{name}'.format(name=member.mailing_list_name)

class MailingListSignupForm(ModelForm):
    captcha = CaptchaField(
        label="Je suis humain",
        help_text="Obligatoire : disponibilité réservée aux humains",
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))
    commune = forms.CharField(
        max_length=100,
        label="Commune", help_text='Nous aide à vous apporter des actualités')
    code_postal = forms.CharField(
        max_length=80,
        label="Code postal", help_text='Obligatoire')
    newsletters = MailingListMMCF(
        queryset=MailingList.objects.filter(list_active=True),
        widget=forms.CheckboxSelectMultiple({'class': 'no-bullet-list'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'captcha',
                  'commune', 'code_postal', 'newsletters')

        labels = {
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Adresse mél",
        }
        help_texts = {
            'first_name': "Obligatoire",
            'last_name': "Obligatoire",
            'email': "Obligatoire",
        }
