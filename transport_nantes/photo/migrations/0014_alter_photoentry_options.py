# Generated by Django 4.0.7 on 2022-10-18 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0013_auto_20221018_1329'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photoentry',
            options={'permissions': (('may_accept_photo', 'May accept photos'), ('may_see_unaccepted_photos', 'May see unaccepted photos')), 'verbose_name': 'Photo Entry', 'verbose_name_plural': 'Photo Entries'},
        ),
    ]