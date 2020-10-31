from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
                             label="Adresse mél", help_text='Obligatoire')
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=254,
                                label="mot de passe", required=False,
                                help_text="Facultatif.  Choisissez un bon : au moins 8 caractères, etc.")
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=254,
                                label="mot de passe", required=False,
                                help_text="Encore la même chose")

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', )

class LoginForm(AuthenticationForm):
    email = forms.EmailField(max_length=254,
                             label="Adresse mél", help_text='Obligatoire')
    password1 = forms.CharField(widget=forms.PasswordInput, max_length=254,
                                label="mot de passe", required=False,
                                help_text="Facultatif, laissez blanc afin de recevoir un mél avec un lien magique.")
    password2 = forms.CharField(widget=forms.PasswordInput, max_length=254,
                                label="mot de passe", required=False,
                                help_text="Encore la même chose.")

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    display_name = forms.CharField(label="Nom d'affichage")

    class Meta:
        model = Profile
        fields = ['display_name']
