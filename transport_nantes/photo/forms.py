from django import forms
from .models import PhotoEntry


class PhotoEntryForm(forms.ModelForm):
    class Meta:
        model = PhotoEntry
        fields = ['category', 'relationship_to_competition', 'photo_location',
                  'photo_kit', 'technical_notes', 'photographer_comments',
                  'submitted_photo']
        widgets = {
            'category': forms.RadioSelect,
            'relationship_to_competition': forms.Textarea,
            'photo_location': forms.TextInput,
            'photo_kit': forms.TextInput,
            'technical_notes': forms.Textarea,
            'photographer_comments': forms.Textarea,
            'submitted_photo': forms.FileInput,
        }