# Generated by Django 3.2.6 on 2021-09-18 02:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectmanager', '0008_auto_20210917_1837'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proyecto',
            name='sprintList',
        ),
        migrations.AddField(
            model_name='sprint',
            name='estado',
            field=models.CharField(choices=[('conf1', 'Carga de Sprint Backlog'), ('conf2', 'Planning Poker'), ('conf3', 'Ultimas Configuraciones'), ('en_desarrollo', 'Sprint en desarrollo')], default='conf1', max_length=20),
        ),
        migrations.AlterField(
            model_name='sprint',
            name='proyecto',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registro_sprints', to='projectmanager.proyecto'),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='desarrolladorAsignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='desarrollador_asignado', to=settings.AUTH_USER_MODEL),
        ),
    ]
