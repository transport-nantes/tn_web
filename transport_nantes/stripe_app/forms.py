from django import forms

class DonationForm(forms.Form):
    mail = forms.EmailField(label="Adresse mail")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    address = forms.CharField(label="Adresse")
    postal_code = forms.CharField(label="Code postal", max_length=5)
