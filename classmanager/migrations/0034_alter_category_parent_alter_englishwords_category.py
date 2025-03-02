# Generated by Django 5.1.4 on 2025-02-24 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "classmanager",
            "0033_category_parentcategory_englishwords_category_parent_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="classmanager.parentcategory",
                verbose_name="親カテゴリ",
            ),
        ),
        migrations.AlterField(
            model_name="englishwords",
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
