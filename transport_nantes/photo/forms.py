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
