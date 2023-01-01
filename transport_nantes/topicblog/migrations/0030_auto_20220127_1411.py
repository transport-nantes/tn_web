# Generated by Django 3.2.11 on 2022-01-27 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("topicblog", "0029_auto_20220126_1335"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="topicblogcontenttype",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="topicblogitem",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="body_image",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="body_text_1_md",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="body_text_2_md",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="body_text_3_md",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="comment",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="cta_1",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="cta_2",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="cta_3",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="header",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="slug",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="social_media",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="template_name",
        ),
        migrations.RemoveField(
            model_name="topicblogtemplate",
            name="title",
        ),
    ]
