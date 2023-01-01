from django import forms


class SignatureForm(forms.Form):
    """Form to generate a mail signature"""

    first_name = forms.CharField(label="Prénom", required=False)
    last_name = forms.CharField(required=False)
    phone_number = forms.CharField(label="Téléphone", required=False)
    role = forms.CharField(label="Fonction", required=False)
