# Generated by Django 3.2 on 2021-10-11 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stripe_app", "0004_merge_20210928_1539"),
    ]

    operations = [
        migrations.AddField(
            model_name="trackingprogression",
            name="tn_session",
            field=models.CharField(
                max_length=50, null=True, verbose_name="Session"
            ),
        ),
    ]
