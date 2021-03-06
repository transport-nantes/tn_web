from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        label="Adresse mél", help_text='Obligatoire')
    captcha = CaptchaField(
        help_text='Obligatoire',
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))
    password1 = forms.CharField(
        widget=forms.PasswordInput, max_length=254,
        label="Mot de passe", required=False,
        help_text="Facultatif")
    password2 = forms.CharField(
        widget=forms.PasswordInput, max_length=254,
        label="Mot de passe", required=False,
        help_text="Encore la même chose")

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse mél")

    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    display_name = forms.CharField(label="Nom d'affichage")

    class Meta:
        model = Profile
        fields = ['display_name']
