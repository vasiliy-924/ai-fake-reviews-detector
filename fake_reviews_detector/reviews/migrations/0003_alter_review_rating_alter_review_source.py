# Generated by Django 4.2.8 on 2025-04-02 20:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0002_alter_analysisresult_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="review",
            name="rating",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="review",
            name="source",
            field=models.CharField(
                max_length=100, verbose_name="Источник (сайт)"),
        ),
    ]
