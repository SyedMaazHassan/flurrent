# Generated by Django 4.1.5 on 2023-06-09 12:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0006_alter_question_options_sectionreport_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='section_reports',
            field=models.ManyToManyField(related_name='main_report', to='surveys.sectionreport'),
        ),
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('point_to_add', models.FloatField()),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='surveys.question')),
            ],
        ),
        migrations.AddField(
            model_name='sectionreport',
            name='suggestions',
            field=models.ManyToManyField(related_name='section_report', to='surveys.suggestion'),
        ),
    ]
