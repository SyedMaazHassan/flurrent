# Generated by Django 4.1.5 on 2023-04-13 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0005_skillcategory_icon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillcategory',
            name='icon',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
    ]
