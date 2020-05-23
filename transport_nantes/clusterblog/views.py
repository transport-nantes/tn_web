from django.views.generic.base import TemplateView
from .models import ClusterBlog, ClusterBlogEntry, ClusterBlogCategory
from django.http import HttpResponseRedirect
from django.urls import reverse

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

    def get(self, request, *args, **kwargs):
        cluster_id = kwargs['cluster']
        category_id = kwargs['category']
        blog = ClusterBlog.objects.get(id=cluster_id)
        entry = ClusterBlogEntry.random_entry(cluster_id, category_id)
        return HttpResponseRedirect(reverse('cluster_blog:deconfinement', args=[entry.slug]))
