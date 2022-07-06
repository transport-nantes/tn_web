from django import forms


class AddressForm(forms.Form):
    address = forms.CharField(max_length=500, label="Adresse")
    city = forms.CharField(max_length=255, label="Ville")
    postcode = forms.CharField(max_length=5, label="Code postal")
