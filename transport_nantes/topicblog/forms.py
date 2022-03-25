from django import forms
from django.forms import ModelForm
from .models import (TopicBlogItem, TopicBlogLauncher,
                     TopicBlogEmail, TopicBlogPress)
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


class TopicBlogLauncherForm(ModelForm):
    """
    Generates a form to create and edit TopicsBlog Launchers objects.
    """

    class Meta:
        model = TopicBlogLauncher
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date')

    field_order = ['slug', 'article_slug', 'campaign_name',
                   'headline', 'template_name', 'launcher_text_md',
                   'launcher_image', 'launcher_image_alt_text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: TopicBlogLauncher

        def get_template_list(self) -> list:

            templates = self.instance.template_config
            template_list = \
                [(None, "Selectionnez un template ...")]
            for template, value in templates.items():
                template_list.append((template, value["user_template_name"]))

            return template_list

        template_list = get_template_list(self)
        self.fields['template_name'] = forms.ChoiceField(
            choices=template_list,
            initial=self.instance.template_name)


class TopicBlogEmailForm(ModelForm):
    """
    Generates a form to create and edit TopicsBlog Email objects.
    """

    class Meta:
        model = TopicBlogEmail
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date')
    field_order = ["slug", "subject", "title", "header_title",
                   "header_description", "header_image", "template_name",
                   "body_text_1_md", "cta_1_slug", "cta_1_label",
                   "body_image_1", "body_image_1_alt_text",
                   "social_description", "twitter_title",
                   "twitter_description", "twitter_image", "og_title",
                   "og_description", "og_image", "author_notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: TopicBlogLauncher

        def get_template_list(self) -> list:

            templates = self.instance.template_config
            template_list = \
                [(None, "Selectionnez un template ...")]
            for template, value in templates.items():
                template_list.append((template, value["user_template_name"]))

            return template_list

        template_list = get_template_list(self)
        self.fields['template_name'] = forms.ChoiceField(
            choices=template_list,
            initial=self.instance.template_name)


class TopicBlogPressForm(ModelForm):
    """
    Generates a form to create and edit TopicsBlog Press objects.
    """

    class Meta:
        model = TopicBlogPress
        # Admins can still edit those values
        exclude = ('first_publication_date', 'publisher', 'user',
                   'publication_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: TopicBlogLauncher

        def get_template_list(self) -> list:

            templates = self.instance.template_config
            template_list = \
                [(None, "Selectionnez un template ...")]
            for template, value in templates.items():
                template_list.append((template, value["user_template_name"]))

            return template_list

        template_list = get_template_list(self)
        self.fields['template_name'] = forms.ChoiceField(
            choices=template_list,
            initial=self.instance.template_name)
