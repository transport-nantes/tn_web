# Generated by Django 3.2.12 on 2022-03-14 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topicblog', '0034_topicbloglauncher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicblogemailsendrecord',
            name='click_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='topicblogemailsendrecord',
            name='open_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='topicblogemailsendrecord',
            name='unsubscribe_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
