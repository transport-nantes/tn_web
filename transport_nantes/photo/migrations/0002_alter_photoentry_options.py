# Generated by Django 3.2.12 on 2022-04-25 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photoentry',
            options={'verbose_name': 'Photo Entry', 'verbose_name_plural': 'Photo Entries'},
        ),
    ]