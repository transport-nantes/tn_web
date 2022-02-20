from django import forms
from .models import PressMention
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, HTML


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("newspaper_name", list="newspaper-names"),
            HTML("<datalist id='newspaper-names'>"
                 "{%for newspaper_name in newspaper_name_list %}"
                 "<option value='{{newspaper_name}}'>"
                 "{% endfor %}"
                 "</datalist>"
                 ),
            Field("article_link"),
            Field("article_title"),
            Field("article_summary"),
            Field("article_publication_date"),
            ButtonHolder(
                Submit('submit', 'Sauvegarder',
                       css_class='btn navigation-button btn-lg btn-block')
            )
        )
