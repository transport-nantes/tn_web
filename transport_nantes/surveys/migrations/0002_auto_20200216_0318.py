# Generated by Django 3.0.3 on 2020-02-16 03:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("surveys", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SurveyCommune",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("commune", models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name="surveyresponder",
            name="commune",
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="email_liste",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="email_person",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="facebook",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="twitter_candidat",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="twitter_liste",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="surveyresponder",
            name="url",
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name="surveyresponder",
            name="commune_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="surveys.SurveyCommune",
            ),
            preserve_default=False,
        ),
    ]
