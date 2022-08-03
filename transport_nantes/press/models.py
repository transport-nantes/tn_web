from django.db import models
from django.urls import reverse
from urllib.parse import urlparse


class PressMention(models.Model):
    class Meta:
        permissions = (
            # Allow the user to see list view and create article
            ("press-editor", "May create and see list view Article"),
        )
        ordering = ['-article_publication_date', 'newspaper_name']

    newspaper_name = models.CharField(max_length=200)
    article_link = models.URLField(max_length=255)
    article_title = models.CharField(max_length=200)
    article_summary = models.TextField()
    article_publication_date = models.DateField()

    # Not all sites have opengraph data.
    og_title = models.CharField(max_length=255, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(
        upload_to="press_mention/open_graph/", blank=True, null=True)

    def __str__(self):
        return f"{self.newspaper_name} {self.article_title}"

    def get_absolute_url(self):
        return reverse("press:detail_item", kwargs={"pk": self.pk})

    def get_domaine_of_link(self):
        return urlparse(self.article_link).netloc
