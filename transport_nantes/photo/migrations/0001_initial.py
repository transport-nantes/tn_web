# Generated by Django 3.2.12 on 2022-04-25 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('EXPERIENCE_PIETON', "L'expérience pieton"), ('NOURRITURE', 'Nourriture')], max_length=80, verbose_name='Catégorie')),
                ('relationship_to_competition', models.TextField(blank=True, verbose_name='Comment cette photo est-elle en relation avec le quartier des Hauts-Pavés ?')),
                ('photo_location', models.CharField(blank=True, max_length=80, verbose_name='Lieu de la photo')),
                ('photo_kit', models.TextField(blank=True, verbose_name='Appareil photo')),
                ('technical_notes', models.TextField(blank=True, verbose_name='Notes techniques')),
                ('photographer_comments', models.TextField(blank=True, verbose_name='Commentaires du photographe')),
                ('submitted_photo', models.ImageField(help_text='résolution minimum : 1800 x 1800', upload_to='photo/', verbose_name='Photo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
