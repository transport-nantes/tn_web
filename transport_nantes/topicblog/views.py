from django.http import Http404
from django.views.generic.base import TemplateView
# from django.shortcuts import render
from .models import TopicBlogPage

class TopicBlogViewTrivial(TemplateView):
    """This is a temporary view that does nothing but render the base
    template.

    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.template_name = 'topicblog/2020_index.html'
        return context

class TopicBlogView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic_slug = kwargs['topic_slug']
        print('topic_slug=', topic_slug)
        for page in TopicBlogPage.objects.all():
            print(page.id, ' - ', page.topic)
        try:
            page = TopicBlogPage.objects.random_topic_member(topic_slug)
        except:
            raise Http404("Page non trouvé (topic inconnu).")

        self.template_name = page.template
        context['page'] = page

        # context[]
        return context
