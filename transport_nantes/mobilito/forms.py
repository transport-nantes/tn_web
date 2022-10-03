from django import forms


class AddressForm(forms.Form):
    location = forms.CharField(label='Localisation', max_length=1000,
                               required=False)
    longitude = forms.FloatField(label='Longitude', widget=forms.HiddenInput(),
                                 required=False)
    latitude = forms.FloatField(label='Latitude', widget=forms.HiddenInput(),
                                required=False)
