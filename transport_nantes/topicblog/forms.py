from django.forms import ModelForm
from .models import TopicBlogItem


class TopicBlogItemForm(ModelForm):

    class Meta:
        model = TopicBlogItem
        # Admins can still edit those values
        exclude = ('item_sort_key', 'servable', 'user', 'published')
