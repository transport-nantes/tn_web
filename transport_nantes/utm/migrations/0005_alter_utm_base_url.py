# Generated by Django 3.2.12 on 2022-03-30 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utm', '0004_auto_20211214_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='utm',
            name='base_url',
            field=models.CharField(max_length=300),
        ),
    ]
