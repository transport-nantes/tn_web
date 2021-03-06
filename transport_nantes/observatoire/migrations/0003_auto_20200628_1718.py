# Generated by Django 3.0.7 on 2020-06-28 17:18

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('observatoire', '0002_observatoire_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='observatoire',
            name='start_date',
            field=models.DateField(default=datetime.date.today()),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='observatoire',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='ObservatoirePerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('validated', models.BooleanField()),
                ('person_name', models.CharField(max_length=100)),
                ('entity', models.CharField(max_length=100)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('twitter', models.CharField(blank=True, max_length=100)),
                ('facebook', models.CharField(blank=True, max_length=100)),
                ('observatoire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='observatoire.Observatoire')),
            ],
        ),
    ]
