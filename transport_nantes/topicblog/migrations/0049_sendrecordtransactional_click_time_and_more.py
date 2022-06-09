# Generated by Django 4.0.4 on 2022-06-09 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('topicblog', '0048_sendrecordtransactional_aws_message_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendrecordtransactional',
            name='click_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sendrecordtransactional',
            name='handoff_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sendrecordtransactional',
            name='open_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='topicblogemailsendrecord',
            name='handoff_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='topicblogpresssendrecord',
            name='handoff_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]