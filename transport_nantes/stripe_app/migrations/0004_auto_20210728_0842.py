# Generated by Django 3.0.7 on 2021-07-28 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_app', '0003_donation_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackingprogression',
            name='step_1',
            field=models.BooleanField(verbose_name='Formulaire montant'),
        ),
        migrations.AlterField(
            model_name='trackingprogression',
            name='step_2',
            field=models.BooleanField(verbose_name='Formulaire informations personnelles'),
        ),
        migrations.AlterField(
            model_name='trackingprogression',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date'),
        ),
    ]
