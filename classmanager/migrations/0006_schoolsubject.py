# Generated by Django 5.1.4 on 2025-01-25 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("classmanager", "0005_remove_studentschool_subjects"),
    ]

    operations = [
        migrations.CreateModel(
            name="SchoolSubject",
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
                (
                    "school",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="classmanager.studentschool",
                        verbose_name="科目",
                    ),
                ),
                (
                    "subject",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="classmanager.subject",
                        verbose_name="科目",
                    ),
                ),
            ],
        ),
    ]
