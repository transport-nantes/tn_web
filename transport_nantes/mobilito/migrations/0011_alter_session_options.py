# Generated by Django 4.0.7 on 2022-09-26 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mobilito", "0010_auto_20220928_0907"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="session",
            options={
                "permissions": (
                    (
                        "session.view_session",
                        "Can view an unpublished session",
                    ),
                )
            },
        ),
    ]
