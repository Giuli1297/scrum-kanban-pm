# Generated by Django 3.2.6 on 2021-11-16 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0005_auto_20211116_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstory',
            name='saldo_horas',
            field=models.FloatField(default=0.0),
        ),
    ]