# Generated by Django 3.2.12 on 2022-03-02 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("mailing_list", "0008_auto_20210214_0901"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mailinglist",
            options={
                "permissions": (
                    (
                        "may_view_list",
                        "May see list of mailing lists and their metrics",
                    ),
                )
            },
        ),
    ]
