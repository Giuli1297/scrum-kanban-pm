# Generated by Django 3.2.6 on 2021-11-16 23:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0008_alter_registroactividaddiairia_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registroactividaddiairia',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
