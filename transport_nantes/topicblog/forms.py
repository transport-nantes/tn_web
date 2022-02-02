from django import forms
from django.forms import ModelForm
from .models import TopicBlogItem


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
