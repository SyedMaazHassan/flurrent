# Generated by Django 4.1.5 on 2023-04-13 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0004_skillcategory_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='skillcategory',
            name='icon',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
