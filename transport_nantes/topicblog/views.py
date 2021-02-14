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
        # print('topic_slug=', topic_slug)
        # for page in TopicBlogPage.objects.all():
        #     print(page.id, ' - ', page.topic)
        try:
            page = TopicBlogPage.objects.random_topic_member(topic_slug)
        except:
            raise Http404("Page non trouvé (topic inconnu).")

        self.template_name = page.template
        context['page'] = page
        context['bullets'] = [
            [page.bullet_image_1, page.bullet_text_1_md],
            [page.bullet_image_2, page.bullet_text_2_md],
            [page.bullet_image_3, page.bullet_text_3_md],
            [page.bullet_image_4, page.bullet_text_4_md],
            [page.bullet_image_5, page.bullet_text_5_md],]
        # print(context['bullets'])
        page.set_context(context)
        print('2>   ', context['social'])
        return context
