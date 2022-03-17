from django.db import models


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

    def __str__(self):
        return f"{self.newspaper_name} {self.article_title}"
