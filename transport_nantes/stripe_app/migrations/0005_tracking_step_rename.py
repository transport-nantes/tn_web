# Generated by Django 3.0.7 on 2021-07-28 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stripe_app', '0004_auto_20210728_0842'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trackingprogression',
            old_name='step_1',
            new_name='amount_form_done',
        ),
        migrations.RenameField(
            model_name='trackingprogression',
            old_name='step_2',
            new_name='donation_form_done',
        ),
    ]
