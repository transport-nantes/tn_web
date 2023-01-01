# Generated by Django 3.2.5 on 2021-12-14 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utm", "0003_rename_session_cookie_utm_session_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="utm",
            name="ua_browser",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_device",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_bot",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_email_client",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_mobile",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_pc",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_table",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_is_touch_capable",
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name="utm",
            name="ua_os",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
