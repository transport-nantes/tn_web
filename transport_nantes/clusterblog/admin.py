from django.contrib import admin
from .models import ClusterBlog, ClusterBlogCategory, ClusterBlogEntry

admin.site.register(ClusterBlog)
admin.site.register(ClusterBlogCategory)
admin.site.register(ClusterBlogEntry)
