from django import forms

class DonationForm(forms.Form):
    mail = forms.EmailField(label="Adresse mail")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    address = forms.CharField(label="Adresse")
    postal_code = forms.CharField(label="Code postal", max_length=5)
    free_amount = forms.IntegerField(label="Montant libre", min_value=1, required=False)

    CHOICES = [ (20, "20 euros"),
                (35, "35 euros"),
                (50, "50 euros"),
                (0, "Montant libre")]
    amount = forms.ChoiceField(label="Je donne une fois",
            choices=CHOICES, widget=forms.RadioSelect, initial=0)
