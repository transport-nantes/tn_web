# Generated by Django 3.2.11 on 2022-01-26 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topicblog', '0028_auto_20220126_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topicblogemail',
            name='template',
        ),
        migrations.RemoveField(
            model_name='topicblogitem',
            name='template',
        ),
    ]