# Generated by Django 4.0.7 on 2022-10-31 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mobilito", "0011_alter_session_options"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Session",
            new_name="MobilitoSession",
        ),
        migrations.AlterModelOptions(
            name="mobilitosession",
            options={
                "permissions": (
                    (
                        "mobilito_session.view_session",
                        "Can view an unpublished session",
                    ),
                )
            },
        ),
        migrations.RenameField(
            model_name="event",
            old_name="session",
            new_name="mobilito_session",
        ),
    ]
