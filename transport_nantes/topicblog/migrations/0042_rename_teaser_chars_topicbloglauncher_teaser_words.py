# Generated by Django 3.2.13 on 2022-05-13 13:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("topicblog", "0041_alter_topicbloglauncher_launcher_image"),
    ]

    operations = [
        migrations.RenameField(
            model_name="topicbloglauncher",
            old_name="teaser_chars",
            new_name="teaser_words",
        ),
    ]
