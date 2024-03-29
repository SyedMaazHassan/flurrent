# Generated by Django 4.1.5 on 2023-01-12 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_review'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AddField(
            model_name='user',
            name='mode',
            field=models.CharField(choices=[('endorser', 'Endorser'), ('organization', 'Organization')], default='organization', max_length=15),
        ),
    ]
