# Generated by Django 4.0.4 on 2022-08-09 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utm", "0005_alter_utm_base_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="utm",
            name="user_is_authenticated",
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
