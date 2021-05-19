# Generated by Django 3.0.7 on 2021-05-05 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=50)),
                ('observatory_name', models.CharField(max_length=50)),
                ('observatory_type', models.CharField(max_length=50)),
                ('layer_name', models.CharField(max_length=50)),
                ('layer_position', models.IntegerField()),
                ('geojson', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('kilometres', models.FloatField()),
            ],
        ),
    ]