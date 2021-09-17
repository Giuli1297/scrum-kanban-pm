# Generated by Django 3.2.6 on 2021-09-15 23:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0002_auto_20210915_1929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proyecto',
            options={'default_permissions': (), 'ordering': ('-fecha_inicio',), 'permissions': (('crear_proyecto', 'Puede crear un proyecto'), ('editar_proyecto', 'Puede editar un proyecto'), ('ver_proyecto', 'Puede ver un proyecto en detalle'), ('ver_proyectos', 'Puede ver proyectos'), ('agregar_smember', 'Puede agregar nuevos Scrum Members'), ('iniciar_proyecto', 'Puede iniciar proyecto'), ('crear_roles_proyecto', 'Puede Crear Roles de Proyecto'), ('ver_roles_proyecto', 'Puede ver roles de proyecto'), ('modificar_roles_proyecto', 'Puede Modificar Roles de Proyecto'), ('eliminar_roles_proyecto', 'Puede eliminar roles de proyecto'), ('importar_roles_proyecto', 'Puede Importar roles de proyecto'), ('ver_user_stories', 'Puede ver user storys'), ('crear_user_stories', 'Puede crear users storys'), ('actualizar_user_stories', 'Puede actualizar users storys'), ('eliminar_user_stories', 'Puede ver users storys'), ('puede_asignar_user_stories', 'Asigna roles a usuarios'), ('puede_quitar_user_stories', 'Quita users storys de usuarios')), 'verbose_name': 'Proyectos'},
        ),
    ]