# Generated by Django 5.1.4 on 2025-02-17 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("classmanager", "0020_school_manageruser"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="studentschool",
            name="school",
        ),
    ]
