# Generated by Django 4.1.5 on 2023-01-07 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_project_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
