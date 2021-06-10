from django import forms

class DonationForm(forms.Form):
    mail = forms.EmailField(label="Adresse mail")
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    address = forms.CharField(label="Adresse")
    postal_code = forms.IntegerField(label="Code postal", max_value=99999)


class AmountForm(forms.Form):
    sub_or_donate = [("subscription", "Je donne tous les mois"),
                     ("payment", "Je donne une fois")]
    donation_type = forms.ChoiceField(  label="Type de don",
                                        choices=sub_or_donate,
                                        widget=forms.RadioSelect)

    CHOICE_PAYMENT = [  (35, "35 euros"),
                        (55, "55 euros"),
                        (95, "95 euros"),
                        (0, "Montant libre")]
    payment_amount = forms.ChoiceField( label="Paiement unique",
                                        choices=CHOICE_PAYMENT,
                                        widget=forms.RadioSelect,
                                        initial=0)

    CHOICE_SUSBCRIPTION = [ ("price_1J0of7ClnCBJWy551iIQ6ydg", "8 euros"),
                            ("price_1J0ogXClnCBJWy552i9Bs2bg", "12 euros"),
                            ("price_1J0ohVClnCBJWy55dAJxHjXE", "20 euros")]
    subscription_amount = forms.ChoiceField(label="Paiement mensuel",
                                            choices=CHOICE_SUSBCRIPTION,
                                            widget=forms.RadioSelect)

    free_amount = forms.IntegerField(label="Montant libre",
                                    min_value=1, required=False)
