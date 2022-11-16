# Generated by Django 4.1.3 on 2022-11-09 10:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("topicblog", "0060_auto_20220829_0948"),
    ]

    operations = [
        migrations.CreateModel(
            name="TopicBlogPanel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(allow_unicode=True, blank=True, max_length=90),
                ),
                ("publication_date", models.DateTimeField(blank=True, null=True)),
                ("first_publication_date", models.DateTimeField(blank=True, null=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                (
                    "scheduled_for_deletion_date",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("template_name", models.CharField(blank=True, max_length=80)),
                ("title", models.CharField(blank=True, max_length=80)),
                ("body_text_1_md", models.TextField(blank=True)),
                ("body_image_1", models.ImageField(blank=True, upload_to="body/")),
                ("body_image_1_alt_text", models.CharField(blank=True, max_length=80)),
                (
                    "publisher",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Panels",
                "permissions": (
                    ("tbpanel.may_view", "May view unpublished TopicBlogPanel"),
                    ("tbpanel.may_edit", "May create and modify TopicBlogPanel"),
                    ("tbpanel.may_publish", "May publish TopicBlogPanel"),
                    ("tbpanel.may_publish_self", "May publish own TopicBlogPanel"),
                ),
            },
        ),
    ]