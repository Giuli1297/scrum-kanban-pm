# Generated by Django 3.2.6 on 2021-10-24 01:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0008_alter_sprint_estado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'default_permissions': (), 'ordering': ('-fecha_inicio',), 'permissions': (('crear_proyecto', 'Puede crear un proyecto'), ('editar_proyecto', 'Puede editar un proyecto'), ('ver_proyecto', 'Puede ver un proyecto en detalle'), ('ver_proyectos', 'Puede ver proyectos'), ('cancelar_proyecto', 'Puede cancelar un proyecto en estado pendiente'), ('gestionar_scrum_members', 'Puede Agregar/Quitar Scrum Members de un proyecto'), ('iniciar_proyecto', 'Puede iniciar proyecto'), ('gestionar_roles_proyecto', 'Puede Agregar/Asignar/Modificar/Eliminar Roles de un Proyecto'), ('importar_roles_proyecto', 'Puede Importar roles de proyecto'), ('gestionar_user_stories', 'Puede Agregar/Modificar/Eliminar User Stories de un proyecto'), ('iniciar_ppoker_proyecto', 'Puede iniciar planning poker de un sprint'), ('estimar_userstory_proyecto', 'Puede estimar User Stories en el Sprint Backlog'), ('cargar_sprint_backlog_proyecto', 'Puede cargar User Stories en el Sprint Backlog'), ('estimar_sprint', 'Puede estimar sprint'), ('realizar_qa', 'Puede realizar QA a user stories'), ('finalizar_sprint', 'Puede finalizar el sprint actual')), 'verbose_name': 'Proyectos'},
        ),
    ]
