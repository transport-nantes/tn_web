# Generated by Django 4.0.4 on 2022-06-20 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("topicblog", "0052_alter_sendrecordmarketingemail_status_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SendRecordTransactionalAdHoc",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("RETRY", "Retry"),
                            ("SENT", "Sent"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                ("handoff_time", models.DateTimeField(blank=True, null=True)),
                ("send_time", models.DateTimeField(blank=True, null=True)),
                ("open_time", models.DateTimeField(blank=True, null=True)),
                ("click_time", models.DateTimeField(blank=True, null=True)),
                (
                    "aws_message_id",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SendRecordTransactionalEmail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("RETRY", "Retry"),
                            ("SENT", "Sent"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                ("handoff_time", models.DateTimeField(blank=True, null=True)),
                ("send_time", models.DateTimeField(blank=True, null=True)),
                ("open_time", models.DateTimeField(blank=True, null=True)),
                ("click_time", models.DateTimeField(blank=True, null=True)),
                (
                    "aws_message_id",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                ("slug", models.SlugField(max_length=200)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SendRecordTransactionalPress",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("RETRY", "Retry"),
                            ("SENT", "Sent"),
                            ("FAILED", "Failed"),
                        ],
                        default="PENDING",
                        max_length=50,
                    ),
                ),
                ("handoff_time", models.DateTimeField(blank=True, null=True)),
                ("send_time", models.DateTimeField(blank=True, null=True)),
                ("open_time", models.DateTimeField(blank=True, null=True)),
                ("click_time", models.DateTimeField(blank=True, null=True)),
                (
                    "aws_message_id",
                    models.CharField(blank=True, max_length=300, null=True),
                ),
                ("slug", models.SlugField(max_length=200)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.DeleteModel(
            name="SendRecordTransactional",
        ),
    ]
