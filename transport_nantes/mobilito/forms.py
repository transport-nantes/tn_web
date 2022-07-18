from django import forms
from django_countries import widgets, countries


class AddressForm(forms.Form):
    address = forms.CharField(
        max_length=500, label=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Adresse'}),
        required=False)

    city = forms.CharField(
        max_length=255, label=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Ville'}),
        required=False)

    postcode = forms.CharField(
        max_length=5,
        label=False,
        widget=forms.TextInput(
            attrs={'placeholder': 'Code postal'}),
        required=False)

    country = forms.ChoiceField(
        widget=widgets.CountrySelectWidget,
        choices=countries,
        initial="FR",
        label=False,
        required=False)
