from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from captcha.fields import CaptchaField
from authentication.models import Profile

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
    monthly = forms.BooleanField(label='Le newsletter mensuel',
                                 required=False)
    quarterly = forms.BooleanField(label='Le newsletter trimestriel',
                                   required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'captcha',
                  'commune', 'code_postal', 'monthly', 'quarterly')

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
