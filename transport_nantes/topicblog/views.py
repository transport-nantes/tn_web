from django.views.generic.base import TemplateView
# from django.shortcuts import render
from .models import TopicBlog

class TopicBlogViewTrivial(TemplateView):
    """This is a temporary view that does nothing but render the base
    template.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = kwargs['base_template']
        self.template_name = 'topicblog/2020.html'
        return context

class TopicBlogView(TemplateView):
    pass
