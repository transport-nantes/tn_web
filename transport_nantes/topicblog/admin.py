from django.contrib import admin
from .models import TopicBlog

class TopicBlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(TopicBlog)
