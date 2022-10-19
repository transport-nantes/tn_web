from captcha.fields import CaptchaField
from django import forms
from .models import PhotoEntry


class PhotoEntryForm(forms.ModelForm):

    terms_and_condition_checkbox = forms.BooleanField(
        label="Je certifie que :",
        required=True,
    )

    class Meta:
        model = PhotoEntry
        fields = ['category', 'submitted_photo', 'photo_location',
                  'photographer_comments', 'relationship_to_competition',
                  'photo_kit', 'technical_notes',
                  'terms_and_condition_checkbox'
                  ]
        widgets = {
            'category': forms.Select,
            'relationship_to_competition': forms.Textarea(
                attrs={
                    'placeholder': ("Exemples : J'y habite, J'y travaille,"
                                    " C'est compliqué, Aucun mais je vous "
                                    "adore, Autres...")
                }),
            'photo_location': forms.Textarea,
            'photo_kit': forms.TextInput,
            'technical_notes': forms.Textarea,
            'photographer_comments': forms.Textarea,
            'submitted_photo': forms.FileInput,
        }


class AnonymousVoteForm(forms.Form):
    """
    Form to collect anonymous votes the first time they vote.
    """
    CHOICES = [("upvote", 'Pour'), ("downvote", 'Contre')]
    vote_value = forms.ChoiceField(
        widget=forms.HiddenInput,
        choices=CHOICES,
        label="Votre vote",
        required=True,
    )
    photoentry_sha1_name = forms.CharField(
        max_length=200, required=True, widget=forms.HiddenInput())
    captcha = CaptchaField(
        # The help text is added here because it's placed below the captcha
        # field. We're adding margin in the template to make it look it's about
        # the next field, placed above it.
        help_text=("Avec votre accord, nous pourrions vous tenir au "
                   "courant du prix populaire et des avancées de la marche"
                   " à pied."),
        required=False,
    )
    email_address = forms.EmailField(
        label="Adresse email :",
        required=False,
        help_text="Facultatif."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photoentry_sha1_name'].widget.attrs['readonly'] = True


class SimpleVoteForm(forms.Form):
    """Form to vote on a single click

    This form is used once the user has voted at least once on any photo entry.
    """
    vote_value = forms.ChoiceField(
        choices=[("upvote", 'Pour'), ("downvote", 'Contre')],
        required=True,
    )


class SimpleVoteFormWithConsent(forms.Form):
    """Form to vote for the first time as a logged in user"""
    vote_value = forms.ChoiceField(
        widget=forms.HiddenInput,
        choices=[("upvote", 'Pour'), ("downvote", 'Contre')],
        required=True,
    )
    consent_box = forms.BooleanField(
        label=("Je préfère ne pas recevoir des nouvelles très occasionnelles"
               " sur les avancées de la marche à pied."),
        required=False,
    )
