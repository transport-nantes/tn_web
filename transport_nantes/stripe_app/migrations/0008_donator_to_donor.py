# Generated by Django 3.0.7 on 2021-07-28 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_app', '0007_donator_to_donor'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Donator',
            new_name='Donor',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='donator',
            new_name='donor',
        ),
    ]
