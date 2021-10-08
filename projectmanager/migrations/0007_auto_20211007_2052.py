# Generated by Django 3.2.6 on 2021-10-07 23:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0006_sprint_horas_realizadas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sprint',
            name='duracion_estimada',
        ),
        migrations.AddField(
            model_name='sprint',
            name='duracion_estimada_dias',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(7), django.core.validators.MaxValueValidator(30)]),
        ),
        migrations.AlterField(
            model_name='sprint',
            name='horas_realizadas',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
