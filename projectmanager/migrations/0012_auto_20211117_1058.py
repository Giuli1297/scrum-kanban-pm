# Generated by Django 3.2.6 on 2021-11-17 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0011_capacidadsmastesprint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='capacidadsmastesprint',
            name='capacidad_horas',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='capacidadsmastesprint',
            name='saldo_horas',
            field=models.FloatField(blank=True, default=models.FloatField(blank=True, null=True), null=True),
        ),
    ]
