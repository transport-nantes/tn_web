from django import forms
from django.forms import ModelForm
from .models import (TopicBlogItem, TopicBlogLauncher,
                     TopicBlogEmail, TopicBlogMailingListPitch,
                     TopicBlogPanel, TopicBlogPress)
from mailing_list.models import MailingList


class ModelFormTemplateList(ModelForm):
    """Render a ModelForm and pre-select template_name field's initial value.

    If a value was already selected (e.g. in case of edit), the value is left
    alone and preselected.
    In case of a new object, the 1st template is pre-selected.

    This class implies an implementation of template_config and that the
    instance has a template_name attribute.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.default_choice = None
        self.set_initial_template()

    def get_template_list(self) -> list:

        templates = self.instance.template_config
        template_list = []
        for template, value in templates.items():
            if not value["active"]:
                continue
            template_list.append((template, value["user_template_name"]))
            if value.get("default_choice", False):
                self.default_choice = template

        return template_list

    def set_initial_template(self):
        template_list = self.get_template_list()
        self.fields['template_name'] = forms.ChoiceField(
                choices=template_list,
                initial=self.default_choice,
            )


class TopicBlogItemForm(ModelFormTemplateList):
    """
    Generates a form to create and edit TopicsBlogItem objects.
    """

    class Meta:
        model = TopicBlogItem
        # Admins can still edit those values
        exclude = ('item_sort_key', 'user',
                   'publication_date', 'first_publication_date', 'publisher',
                   'scheduled_for_deletion_date')


class TopicBlogEmailSendForm(forms.Form):
    """
    Generates a form that shows available mailing lists to send
    a given sendable TopicBlog object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_mailing_lists = MailingList.objects.all().values(
            "mailing_list_name", "mailing_list_token")
        self.all_mailing_lists = \
            [(item["mailing_list_token"], item["mailing_list_name"])
             for item in self.all_mailing_lists]
        # Add a default value
        self.all_mailing_lists.insert(
            0, (None, "Selectionnez une liste d'envoi ..."))
        self.fields["mailing_list"].choices = self.all_mailing_lists

    mailing_list = forms.ChoiceField(
        choices=[],
        label="Liste d'envoi",
        required=True)

    confirmation_box = forms.BooleanField(
        label="Confirmer l'envoi",
        required=True)


class TopicBlogLauncherForm(ModelFormTemplateList):
    """
    Generates a form to create and edit TopicsBlog Launchers objects.
    """

    class Meta:
        model = TopicBlogLauncher
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date', 'scheduled_for_deletion_date')

    field_order = ['slug', 'article_slug', 'campaign_name',
                   'headline', 'template_name', 'launcher_text_md',
                   'launcher_image', 'launcher_image_alt_text']


class TopicBlogEmailForm(ModelFormTemplateList):
    """
    Generates a form to create and edit TopicsBlog Email objects.
    """

    class Meta:
        model = TopicBlogEmail
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date', 'scheduled_for_deletion_date')
    field_order = ["slug", "subject", "title", "header_title",
                   "header_description", "header_image", "template_name",
                   "body_text_1_md", "cta_1_slug", "cta_1_label",
                   "body_image_1", "body_image_1_alt_text",
                   "social_description", "twitter_title",
                   "twitter_description", "twitter_image", "og_title",
                   "og_description", "og_image", "author_notes"]


class TopicBlogPressForm(ModelFormTemplateList):
    """
    Generates a form to create and edit TopicsBlog Press objects.
    """

    class Meta:
        model = TopicBlogPress
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date', 'scheduled_for_deletion_date')


class TopicBlogPanelForm(ModelFormTemplateList):
    """Generates a form to create and edit TopicBlogPanel objects."""

    class Meta:
        model = TopicBlogPanel
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date', 'scheduled_for_deletion_date')


class TopicBlogMailingListPitchForm(ModelFormTemplateList):
    """ Generates a form to create and edit TopicBlogMailingList objects.
    """

    class Meta:
        model = TopicBlogMailingListPitch
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date', 'scheduled_for_deletion_date')


class SendToSelfForm(forms.Form):
    """Form to send a TopicBlog object to oneself"""
    sent_object_class = forms.CharField(required=True)
    sent_object_id = forms.IntegerField(required=True)
    sent_object_transactional_send_record_class = forms.CharField(
        required=True)
    redirect_url = forms.CharField(required=True)
