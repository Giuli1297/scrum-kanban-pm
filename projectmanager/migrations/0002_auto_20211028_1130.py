# Generated by Django 3.2.6 on 2021-10-28 14:30

from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projectmanager', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'default_permissions': (), 'ordering': ('-fecha_inicio',), 'permissions': (('crear_proyecto', 'Puede crear un proyecto'), ('editar_proyecto', 'Puede editar un proyecto'), ('ver_proyecto', 'Puede ver un proyecto en detalle'), ('ver_proyectos', 'Puede ver proyectos'), ('cancelar_proyecto', 'Puede cancelar un proyecto en estado pendiente'), ('gestionar_scrum_members', 'Puede Agregar/Quitar Scrum Members de un proyecto'), ('iniciar_proyecto', 'Puede iniciar proyecto'), ('gestionar_roles_proyecto', 'Puede Agregar/Asignar/Modificar/Eliminar Roles de un Proyecto'), ('importar_roles_proyecto', 'Puede Importar roles de proyecto'), ('gestionar_user_stories', 'Puede Agregar/Modificar/Eliminar User Stories de un proyecto'), ('iniciar_ppoker_proyecto', 'Puede iniciar planning poker de un sprint'), ('estimar_userstory_proyecto', 'Puede estimar User Stories en el Sprint Backlog'), ('cargar_sprint_backlog_proyecto', 'Puede cargar User Stories en el Sprint Backlog'), ('estimar_sprint', 'Puede estimar sprint'), ('realizar_qa', 'Puede realizar QA a user stories'), ('finalizar_sprint', 'Puede finalizar el sprint actual')), 'verbose_name': 'Proyectos'},
        ),
        migrations.AlterModelOptions(
            name='userstory',
            options={'ordering': ['estado', '-prioridad'], 'permissions': (('desarrollar_user_story', 'Puede desarrollar un user story'),), 'verbose_name': 'User Story', 'verbose_name_plural': 'Users Storys'},
        ),
        migrations.AddField(
            model_name='historialus',
            name='descripcionDone',
            field=models.TextField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='historialus',
            name='idUs',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='historialus',
            name='prioridad',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='sprint',
            name='duracion_restante_dias',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sprint',
            name='saved_horas_us_total',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sprint',
            name='saved_us_progress',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='userstory',
            name='descripcionDone',
            field=models.TextField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='sprint',
            name='estado',
            field=models.CharField(choices=[('conf1', 'Carga de Sprint Backlog'), ('conf2', 'Planning Poker'), ('conf3', 'Sprint en desarrollo'), ('fin', 'Sprint finalizado')], default='conf1', max_length=20),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='desarrolladorAsignado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='desarrollador_asignado', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='estado',
            field=models.CharField(choices=[('Nuevo', 'Nuevo'), ('no-terminado', 'No Terminado'), ('To-Do', 'To-Do'), ('Doing', 'Doing'), ('Done', 'Done'), ('QA', 'QA'), ('Release', 'Release')], default='Nuevo', max_length=20),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='tiempoEnDesarrollo',
            field=models.FloatField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='userstory',
            name='tiempoEstimado',
            field=models.FloatField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.CreateModel(
            name='QA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now=True)),
                ('comentario', models.TextField(max_length=255)),
                ('aceptar', models.BooleanField(default=False)),
                ('user_story', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='QA', to='projectmanager.userstory')),
            ],
        ),
        migrations.CreateModel(
            name='logHistorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(blank=True, max_length=255)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('us', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logHistorial', to='projectmanager.userstory')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
