from django import forms
from .models import PressMention

class PressMentionForm(forms.ModelForm):
    class Meta:
        model = PressMention
        fields = "__all__"
    newspaper_name = forms.CharField(max_length=200, label="Nom du journal")
    article_link = forms.URLField(max_length=255, label="Lien de l'article")
    article_title = forms.CharField(max_length=200, label="Titre de l'article")
    article_summary = forms.CharField(
        max_length=200, label="Description de l'article",
        widget=forms.Textarea)
    article_publication_date = forms.DateField(
        label="Date de pubication de l'article",
        widget=forms.TextInput(attrs={'type': 'date'}))
