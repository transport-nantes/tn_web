# Generated by Django 3.2.13 on 2022-05-17 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topicblog', '0043_rename_teaser_words_topicbloglauncher_teaser_chars'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicblogpresssendrecord',
            name='click_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='topicblogpresssendrecord',
            name='open_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='topicblogpresssendrecord',
            name='unsubscribe_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]