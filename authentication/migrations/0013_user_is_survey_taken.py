# Generated by Django 4.1.5 on 2023-05-24 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_alter_user_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_survey_taken',
            field=models.BooleanField(default=False),
        ),
    ]