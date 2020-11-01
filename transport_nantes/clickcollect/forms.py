from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from captcha.fields import CaptchaField

class ClickCollectForm(ModelForm):
    first_name = forms.CharField(
        max_length=80,
        label="Prénom", help_text='Obligatoire')
    last_name = forms.CharField(
        max_length=80,
        label="Nom", help_text='Obligatoire')
    email = forms.EmailField(
        max_length=254,
        label="Adresse mél", help_text='Obligatoire')
    captcha = CaptchaField(
        label="Je suis humain",
        help_text="Obligatoire : disponibilité réservée aux humains",
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'captcha',)

