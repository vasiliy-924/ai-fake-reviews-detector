# Generated by Django 5.1.7 on 2025-03-30 18:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="analysisresult",
            name="review",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="analysis",
                to="reviews.review",
            ),
        ),
    ]
