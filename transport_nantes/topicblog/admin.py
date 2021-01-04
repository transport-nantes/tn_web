from django.contrib import admin
from .models import TopicBlogPage

class TopicBlogPageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(TopicBlogPage, TopicBlogPageAdmin)
