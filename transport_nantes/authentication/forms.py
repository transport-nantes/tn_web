from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from .models import Profile

class EmailLoginForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=254,
        label="Adresse mail", help_text='Obligatoire')
    captcha = CaptchaField(
        help_text='Obligatoire',
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))
    remember_me = forms.BooleanField(
        label="Se souvenir de moi",
        required=False)

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.EMAIL_FIELD in self.fields:
            self.fields[self._meta.model.EMAIL_FIELD].widget.attrs['autofocus'] = True


class PasswordLoginForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=254,
        label="Adresse mail", help_text='Obligatoire')
    remember_me = forms.BooleanField(
        label="Se souvenir de moi",
        required=False)
    password = forms.CharField(
        widget=forms.PasswordInput, max_length=254,
        label="Mot de passe", required=False,
        help_text="au moins 8 caractères", min_length=8,
        error_messages=dict(min_length="Le mot de passe doit faire plus de 8 caractères"))

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['autofocus'] = True


class OtherForm:
    password1 = forms.CharField(
        widget=forms.PasswordInput, max_length=254,
        label="Mot de passe", required=False,
        help_text="Facultatif", min_length=8,
        error_messages=dict(min_length="Le mot de passe doit faire plus de 8 caractères"))
    password2 = forms.CharField(
        widget=forms.PasswordInput, max_length=254,
        label="Mot de passe", required=False,
        help_text="Encore la même chose", min_length=8,
        error_messages=dict(min_length="Le mot de passe doit faire plus de 8 caractères"))

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse mail")

    class Meta:
        model = User
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):
    display_name = forms.CharField(label="Nom d'affichage")

    class Meta:
        model = Profile
        fields = ['display_name']
