# Generated by Django 3.2.11 on 2022-03-18 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('press', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pressmention',
            options={'ordering': ['-article_publication_date', 'newspaper_name'], 'permissions': (('press-editor', 'May create and see list view Article'),)},
        ),
        migrations.CreateModel(
            name='OpenGraphTwitter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('og_title', models.CharField(blank=True, max_length=255)),
                ('og_description', models.TextField(blank=True)),
                ('og_image', models.URLField(blank=True, max_length=255)),
                ('twitter_title', models.CharField(blank=True, max_length=255)),
                ('twitter_description', models.TextField(blank=True)),
                ('twitter_image', models.URLField(blank=True, max_length=255)),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('press_mention', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='press.pressmention')),
            ],
        ),
    ]
