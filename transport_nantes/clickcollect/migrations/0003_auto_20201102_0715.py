# Generated by Django 3.0.7 on 2020-11-02 07:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clickcollect', '0002_auto_20201102_0713'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clickandcollect',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
