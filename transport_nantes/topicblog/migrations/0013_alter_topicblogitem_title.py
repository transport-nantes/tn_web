# Generated by Django 3.2.5 on 2021-10-17 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("topicblog", "0012_alter_topicblogitem_item_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="topicblogitem",
            name="title",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
