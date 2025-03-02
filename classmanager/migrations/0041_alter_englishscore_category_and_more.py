# Generated by Django 5.1.4 on 2025-03-02 11:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classmanager", "0040_transgamescore_cleartime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="englishscore",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="classmanager.category",
                verbose_name="カテゴリ",
            ),
        ),
        migrations.AlterField(
            model_name="transgamescore",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="classmanager.category",
                verbose_name="カテゴリ",
            ),
        ),
    ]
