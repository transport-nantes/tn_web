# Generated by Django 4.0.7 on 2022-09-26 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobilito', '0006_remove_session_address_remove_session_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='published',
            field=models.BooleanField(default=True),
        ),
    ]