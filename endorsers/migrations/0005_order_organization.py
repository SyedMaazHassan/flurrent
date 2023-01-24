# Generated by Django 4.1.5 on 2023-01-22 16:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0005_productservice_thumbnail'),
        ('endorsers', '0004_order_approval_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.organization'),
        ),
    ]
