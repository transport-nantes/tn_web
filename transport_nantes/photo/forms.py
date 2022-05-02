from django import forms
from .models import PhotoEntry


class PhotoEntryForm(forms.ModelForm):
    class Meta:
        model = PhotoEntry
        fields = ['category', 'submitted_photo', 'photo_location',
                  'photographer_comments', 'relationship_to_competition',
                  'photo_kit', 'technical_notes',
                  ]
        widgets = {
            'category': forms.Select,
            'relationship_to_competition': forms.Textarea(
                attrs={
                    'placeholder': ("Exemples : j'y habite, j'y travaille,"
                                    " c'est compliqué, autre...")
                }),
            'photo_location': forms.Textarea,
            'photo_kit': forms.TextInput,
            'technical_notes': forms.Textarea,
            'photographer_comments': forms.Textarea,
            'submitted_photo': forms.FileInput,
        }
