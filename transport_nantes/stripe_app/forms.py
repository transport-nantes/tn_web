from django import forms

# import a widget to allow to pick a country list
from django_countries import widgets, countries

# crispy forms allows to manage layout of forms as well as styles
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (ButtonHolder, HTML, Submit,
                                Layout, Row, Column, Field, Button)



class DonationForm(forms.Form):

    gender = forms.ChoiceField( label="",
                                choices=[("M", "M"), ("MME", "MME")],
                                widget=forms.RadioSelect)

    first_name = forms.CharField(label="Prénom",
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Prénom*'}))

    last_name = forms.CharField(label="Nom",
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Nom*'}))

    mail = forms.EmailField(label="Adresse mail",
                            widget=forms.EmailInput(
                                attrs={'placeholder': 'Adresse e-mail*'}))

    address = forms.CharField(  label="Adresse",
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Adresse postale*'}))

    more_address = forms.CharField(label="Complément d'adresse",
                                   widget=forms.TextInput(
                                       attrs={'placeholder': "Complément d'adresse"}),
                                   required=False)

    postal_code = forms.IntegerField(label="Code postal",
                                    max_value=99999,
                                    widget=forms.TextInput(
                                        attrs={'placeholder': 'Code postal*'}))

    city = forms.CharField(label="Ville",
                            widget=forms.TextInput(
                                attrs={'placeholder': 'Ville*'}))

    cell_phone = forms.CharField(label="Téléphone",
                                 widget=forms.TextInput(
                                     attrs={'placeholder': 'Téléphone'}),
                                 max_length=50, required=False)

    country = forms.ChoiceField(
        widget=widgets.CountrySelectWidget, choices=countries, initial="FR")

    consent = forms.BooleanField(
        label="J'accepte les règles de conditions générales \
            et de la visite de la plateforme",)
    data_collect = forms.BooleanField(label="J'accepte que mes données soient\
            collectées à des fins d'analyse et dans le cadre d'une prise de\
            contact de la part des Mobilitains")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_show_labels= False

        self.helper.layout = Layout(
            ButtonHolder(
                Button("toStep1", "Revenir à l'étape précédente",
                    css_id="toStep1",
                    css_class="btn-outline-info",
                    style="margin-bottom: 1em"),
            ),
            Field("gender", template="stripe_app/inline_radio_custom.html", id="gender"),
            Row(
                Column("first_name"),
                Column("last_name")
            ),
            Row(
                Column("mail"),
                Column("cell_phone")
            ),
            HTML("<br />"),
            "address",
            "more_address",
            Row(
                Column("postal_code"),
                Column("city"),
            ),
            "country",
            Field("consent", template="stripe_app/checkbox_custom.html"),
            Field("data_collect", template="stripe_app/checkbox_custom.html"),
            Submit("submit", "Soutenir",
                    css_id="supportButton",
                    css_class="btn-success"),
        )

class AmountForm(forms.Form):
    sub_or_donate = [("subscription", "Je donne tous les mois"),
                     ("payment", "Je donne une fois")]
    donation_type = forms.ChoiceField(  label="",
                                        choices=sub_or_donate,
                                        widget=forms.RadioSelect)

    CHOICE_PAYMENT = [  (35, "35 euros"),
                        (55, "55 euros"),
                        (95, "95 euros"),
                        (0, "Montant libre")]
    payment_amount = forms.ChoiceField( label="",
                                        choices=CHOICE_PAYMENT,
                                        widget=forms.RadioSelect)

    CHOICE_SUSBCRIPTION = [ ("price_1J0of7ClnCBJWy551iIQ6ydg", "8 euros"),
                            ("price_1J0ogXClnCBJWy552i9Bs2bg", "12 euros"),
                            ("price_1J0ohVClnCBJWy55dAJxHjXE", "20 euros")]
    subscription_amount = forms.ChoiceField(label="",
                                            choices=CHOICE_SUSBCRIPTION,
                                            widget=forms.RadioSelect)

    free_amount = forms.IntegerField(label="Montant libre",
                                    min_value=1, required=False,
                                    widget=forms.TextInput(
                                     attrs={'placeholder': 'Montant libre'}),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_show_labels= False

        self.helper.layout = Layout(
            Field("donation_type",
                    template="stripe_app/inline_radio_custom.html"),
            Field("subscription_amount",
                    template="stripe_app/inline_radio_custom.html",
                    id="subscription_amount_rb", style="display: none"),
            Field("payment_amount",
                    template="stripe_app/inline_radio_custom.html",
                    id="payment_amount_rb", style="display: none"),
            Field("free_amount", id="free_amount", style="display: none"),
            ButtonHolder(
                Submit('submit', 'Continuer',
                        css_class='btn btn-primary', css_id="toStep2")
            )
        )
