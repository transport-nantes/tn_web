from django import forms
from django.forms import ModelForm
from .models import TopicBlogItem
from mailing_list.models import MailingList


class TopicBlogItemForm(ModelForm):
    """
    Generates a form to create and edit TopicsBlogItem objects.
    """

    class Meta:
        model = TopicBlogItem
        # Admins can still edit those values
        exclude = ('item_sort_key', 'servable', 'user',
                   'publication_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: TopicBlogItem

        # When an item is published, its slug becomes frozen (unmodifiable).
        if self.instance.publication_date:
            self.fields['slug'].widget.attrs['readonly'] = True

        def get_template_list(self) -> list:

            templates = self.instance.template_config
            template_list = \
                [(None, "Selectionnez un template ...")]
            for template, value in templates.items():
                template_list.append((template, value["user_template_name"]))

            return template_list

        template_list = get_template_list(self)
        self.fields['template'] = forms.ChoiceField(
            choices=template_list,
            initial=self.instance.template_name)


class TopicBlogEmailSendForm(forms.Form):
    """
    Generates a form that shows available mailing lists to send
    a given TBEmail.
    """
    # Get a list of mailing lists with their names and tokens
    all_mailing_lists = MailingList.objects.all().values(
        "mailing_list_name", "mailing_list_token")
    all_mailing_lists = \
        [(item["mailing_list_token"], item["mailing_list_name"])
         for item in all_mailing_lists]
    # Add a default value
    all_mailing_lists.insert(0, (None, "Selectionnez une liste d'envoi ..."))

    mailing_list = forms.ChoiceField(
        choices=all_mailing_lists,
        label="Liste d'envoi",
        required=True)
