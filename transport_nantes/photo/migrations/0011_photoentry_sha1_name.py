# Generated by Django 4.0.7 on 2022-10-18 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0010_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='photoentry',
            name='sha1_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
