# Generated by Django 5.1.6 on 2025-02-17 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0006_subjectspecialization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
