# Generated by Django 4.1.5 on 2023-03-09 16:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("endorsers", "0010_endorser_rating"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="endorser",
            name="reviews",
        ),
    ]