from django import forms
from .models import PressMention
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, HTML, Row


class PressMentionForm(forms.ModelForm):
    class Meta:
        model = PressMention
        fields = "__all__"
    newspaper_name = forms.CharField(max_length=1000, label="Nom du journal")
    article_link = forms.URLField(max_length=1000, label="Lien de l'article")
    article_title = forms.CharField(max_length=1000, label="Titre de l'article")
    article_summary = forms.CharField(
        max_length=1000, label="Description de l'article",
        widget=forms.Textarea)
    article_publication_date = forms.DateField(
        label="Date de pubication de l'article",
        widget=forms.TextInput(attrs={'type': 'date'}),
        initial=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("article_link"),
            Field("newspaper_name", list="newspaper-names"),
            HTML("<datalist id='newspaper-names'>"
                 "{%for newspaper_name in newspaper_name_list %}"
                 "<option value='{{newspaper_name}}'>"
                 "{% endfor %}"
                 "</datalist>"
                 ),
            Field("article_title"),
            Field("article_summary"),
            Field("article_publication_date"),
            ButtonHolder(
                Submit('submit', 'Sauvegarder',
                       css_class='btn navigation-button btn-lg btn-block')
            )
        )


class PressMentionSearch(forms.Form):
    newspaper_name_search = forms.CharField(
        label='Nom du journal', max_length=1000, required=False)
    article_link = forms.CharField(
        label="Lien de l'article", max_length=1000, required=False)
    article_title = forms.CharField(
        label="Titre de l'article", max_length=1000, required=False)
    article_summary = forms.CharField(
        label="Description de l'article", required=False)
    article_date_start = forms.DateField(
        label="Date de début", required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),)
    article_date_end = forms.DateField(
        label="Date de fin", required=False,
        widget=forms.DateInput(attrs={'type': 'date'}))
    search = forms.ChoiceField(initial=True, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.layout = Layout(
            Field("search"),
            Row(Field("newspaper_name_search", list="newspaper-names",
                      wrapper_class='col-6 col-md-4'),
                Field("article_link", wrapper_class='col-6 col-md-4'),
                Field("article_title", wrapper_class='col-6 col-md-4'),
                Field("article_summary", wrapper_class='col-6 col-md-4'),
                Field("article_date_start", wrapper_class='col-6 col-md-4'),
                Field("article_date_end", wrapper_class='col-6 col-md-4'),

                ),
            Row(
                HTML("<div class='col-6'>"
                     "<button class='btn navigation-button btn-lg btn-block'>"
                     "Recherche"
                     "</button></div>"),
                HTML("<div class='col-6'>"
                     "<a href='{% url 'press:list_items' %}'"
                     "class='btn navigation-button btn-lg btn-block'>"
                     "Réinitialiser"
                     "<a></div>"
                     ),
                css_class="my-2"
            ),
        )
