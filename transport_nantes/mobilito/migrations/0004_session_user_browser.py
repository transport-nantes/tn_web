# Generated by Django 4.0.4 on 2022-07-19 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilito', '0003_alter_session_address_alter_session_bicycle_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='user_browser',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
