from django.views.generic.base import TemplateView
from .models import ClusterBlog, ClusterBlogEntry, ClusterBlogCategory

# Create your views here.

class MainClusterBlog(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = ClusterBlog.objects.get(clusterblogentry__slug=context['slug'])
        self.template_name = blog.template_name
        context['blog'] = blog
        context['categories'] = ClusterBlogCategory.objects.all().filter(cluster=blog.pk)
        context['entry'] = ClusterBlogEntry.objects.get(slug=context['slug'])
        return context

class CategoryClusterBlog(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('>> ', context)
        blog = ClusterBlog.objects.get(id=context['cluster'])
        self.template_name = blog.template_name
        context['blog'] = blog
        context['categories'] = ClusterBlogCategory.objects.all().filter(cluster=blog.pk)
        context['entry'] = ClusterBlogEntry.random_entry(context['cluster'], context['category'])
        return context
