from django.forms import ModelForm
from django.forms.models import ModelChoiceField
from .models import TopicBlogItem, TopicBlogTemplate


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

        # self.data is the POST data
        if 'template' in self.data:
            try:
                template_id = int(self.data.get('template'))
                # Sets the list of valid inputs to be this queryset
                self.fields['template'].queryset = \
                    TopicBlogTemplate.objects.filter(id=template_id)
            except (ValueError, TypeError):
                # invalid input from the client
                # ignore and fallback to empty queryset
                pass
