# Generated by Django 3.2.5 on 2021-12-11 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topicblog', '0022_alter_topicblogitem_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topicblogitem',
            options={'permissions': (('tbi.may_view', 'May view unpublished TopicBlogItems'), ('tbi.may_edit', 'May create and modify TopicBlogItems'), ('tbi.may_publish', 'May publish TopicBlogItems'), ('tbi.may_publish_self', 'May publish own TopicBlogItems'), ('tbi.may_retire_self', 'May retire own TopicBlogItems'), ('tbi.may_retire', 'May retire TopicBlogItems'))},
        ),
    ]