from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, Form
from captcha.fields import CaptchaField
from .models import MailingList
from crispy_forms.helper import FormHelper


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
        help_text="* disponibilité réservée aux humains",
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))
    commune = forms.CharField(
        max_length=100,
        required=False,
        label="Commune", help_text='Nous aide à vous apporter des actualités')
    code_postal = forms.CharField(
        max_length=80,
        required=False,
        label="Code postal",
        help_text='Nous aide à vous apporter des actualités')
    newsletters = MailingListMMCF(
        queryset=MailingList.objects.filter(list_active=True,
                                            is_petition=False),
        widget=forms.CheckboxSelectMultiple({'class': 'no-bullet-list'}),
        label="Je m’inscris :")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'captcha',
                  'commune', 'code_postal', 'newsletters')

        labels = {
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Adresse mail",
        }
        help_texts = {
            'first_name': "* Obligatoire",
            'last_name': "* Obligatoire",
            'email': "* Obligatoire",
        }


# Form for subscribe or unsubscribe auth required
class SubscribeUpdateForm(Form):
    mailinglist = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.HiddenInput())

# First step of quick signup to the newsletter


class FirstStepQuickMailingListSignupForm(Form):
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={'placeholder': 'Votre adresse e-mail *'}))
    mailinglist = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False

# Like MailingListSignupForm, but only requests email.


class QuickMailingListSignupForm(ModelForm):
    captcha = CaptchaField(
        label="Je suis humain",
        help_text="* disponibilité réservée aux humains",
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"),
        required=True)
    mailinglist = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('email', 'captcha', 'mailinglist')

        labels = {
            'email': "Adresse mail",
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email == "":
            self.add_error('email', "Vous devez entrer une adresse mail")

        return cleaned_data


class QuickPetitionSignupForm(ModelForm):
    captcha = CaptchaField(
        label="Je suis humain",
        help_text="* disponibilité réservée aux humains",
        error_messages=dict(invalid="captcha incorrect, veuillez réessayer"))
    petition_name = forms.CharField(
        max_length=80,
        required=False,  # True
        widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'captcha')

        labels = {
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Adresse mail",
        }
