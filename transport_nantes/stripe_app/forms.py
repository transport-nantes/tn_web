from django import forms

# import a widget to allow to pick a country list
from django_countries import widgets, countries

# crispy forms allows to manage layout of forms as well as styles
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (ButtonHolder, HTML, Submit,
                                 Layout, Row, Column, Field, Button)

# These forms are used to collect donors data.
# The overall look is handled by the Crispy forms framework.
# Documentation available here:
# https://django-crispy-forms.readthedocs.io/en/latest/


class DonationForm(forms.Form):

    first_name = forms.CharField(label="Prénom",
                                 widget=forms.TextInput(
                                    attrs={'placeholder': 'Prénom*'}))

    last_name = forms.CharField(label="Nom",
                                widget=forms.TextInput(
                                    attrs={'placeholder': 'Nom*'}))

    mail = forms.EmailField(label="Adresse mail",
                            widget=forms.EmailInput(
                                attrs={'placeholder': 'Adresse e-mail*'}))

    address = forms.CharField(label="Adresse",
                              widget=forms.TextInput(
                                    attrs={'placeholder': 'Adresse postale*'}))

    more_address = forms.CharField(label="Complément d'adresse",
                                   widget=forms.TextInput(
                                       attrs={'placeholder': "Complément d'adresse"}), # noqa
                                   required=False)

    postal_code = forms.CharField(label="Code postal",
                                  widget=forms.TextInput(
                                        attrs={'placeholder': 'Code postal*'}))

    city = forms.CharField(label="Ville",
                           widget=forms.TextInput(
                                attrs={'placeholder': 'Ville*'}))

    country = forms.ChoiceField(
        widget=widgets.CountrySelectWidget, choices=countries, initial="FR")

    data_collect = forms.BooleanField(label="J'accepte que mes données soient \
        collectées afin de traiter mon don et de communiquer avec moi à ce \
        sujet par la suite.  Je comprends que je peux à tout moment demander \
        à ne plus être contacté(e).")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_show_labels = False

        # Layout class handles the layout of the form.
        # Documentation: https://django-crispy-forms.readthedocs.io/en/latest/api_layout.html # noqa
        self.helper.layout = Layout(
            ButtonHolder(
                Button("toStep1", "Revenir à l'étape précédente",
                       css_id="toStep1",
                       css_class="btn-outline-info",
                       style="margin-bottom: 1em"),
            ),
            Row(
                Column("first_name"),
                Column("last_name")
            ),
            "mail",
            HTML("<br />"),
            "address",
            "more_address",
            Row(
                Column("postal_code"),
                Column("city"),
            ),
            "country",
            Field("data_collect", template="stripe_app/checkbox_custom.html"),
            Submit("submit", "Soutenir",
                   css_id="supportButton",
                   css_class="btn-success"),
        )


class AmountForm(forms.Form):
    sub_or_donate = [("payment", "Je donne une fois"),
                     ("subscription", "Je donne tous les mois")]
    donation_type = forms.ChoiceField(label="",
                                      choices=sub_or_donate,
                                      widget=forms.RadioSelect)

    # Initialized in views.py by get_amount_choices()
    payment_amount = forms.ChoiceField(label="",
                                       choices=[],
                                       widget=forms.RadioSelect)

    # initialized in views.py by get_subscription_amounts()
    subscription_amount = forms.ChoiceField(label="",
                                            choices=[],
                                            widget=forms.RadioSelect)

    free_amount = forms.IntegerField(label="Montant libre",
                                     min_value=1, required=False,
                                     widget=forms.TextInput(
                                         attrs={'placeholder': 'Montant libre'}),) # noqa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_show_labels = False

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
            HTML("<p id='real_cost'></p>"),
            ButtonHolder(
                Submit('submit', 'Continuer',
                       css_class='btn btn-primary', css_id="toStep2")
            )
        )
