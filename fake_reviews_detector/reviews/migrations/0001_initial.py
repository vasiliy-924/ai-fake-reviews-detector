# Generated by Django 5.1.7 on 2025-03-28 19:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст отзыва")),
                (
                    "source",
                    models.CharField(
                        max_length=100, verbose_name="Источник (Яндекс.Маркет и т.д.)"
                    ),
                ),
                ("rating", models.IntegerField(blank=True, null=True)),
                ("date_created", models.DateTimeField(auto_now_add=True)),
                ("is_verified", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="AnalysisResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_fake", models.BooleanField(verbose_name="Фейковый?")),
                ("probability", models.FloatField(
                    verbose_name="Вероятность (0-1)")),
                ("details", models.JSONField(default=dict)),
                (
                    "review",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analisis",
                        to="reviews.review",
                    ),
                ),
            ],
        ),
    ]
