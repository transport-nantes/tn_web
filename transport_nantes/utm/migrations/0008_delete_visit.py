# Generated by Django 4.0.4 on 2022-09-19 06:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utm', '0007_rename_utm_visit'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Visit',
        ),
    ]
