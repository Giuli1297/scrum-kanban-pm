# Generated by Django 3.2.6 on 2021-09-19 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectmanager', '0002_alter_proyecto_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserWorkTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.CharField(choices=[('LUN', 'LUNES'), ('MAR', 'MARTES'), ('MIE', 'MIERCOLES'), ('JUE', 'JUEVES'), ('VIE', 'VIERNES')], max_length=20)),
                ('horas', models.FloatField(default=0.0)),
                ('desarrollador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiempos_de_trabajo', to=settings.AUTH_USER_MODEL)),
                ('proyecto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiempos_de_usuarios', to='projectmanager.proyecto')),
            ],
        ),
    ]
