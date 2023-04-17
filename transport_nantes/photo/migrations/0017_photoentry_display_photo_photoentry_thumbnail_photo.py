# Generated by Django 4.1.7 on 2023-04-17 13:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("photo", "0016_photoentry_photographer_identifier"),
    ]

    operations = [
        migrations.AddField(
            model_name="photoentry",
            name="display_photo",
            field=models.ImageField(blank=True, upload_to="photo/"),
        ),
        migrations.AddField(
            model_name="photoentry",
            name="thumbnail_photo",
            field=models.ImageField(blank=True, upload_to="photo/"),
        ),
    ]
