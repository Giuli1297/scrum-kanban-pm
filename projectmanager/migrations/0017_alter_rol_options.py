# Generated by Django 3.2.6 on 2021-09-03 07:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectmanager', '0016_alter_rol_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rol',
            options={'ordering': ['name'], 'permissions': (('ver_roles', 'Puede ver roles'), ('crear_roles', 'Puede crear roles'), ('actualizar_roles', 'Puede actualizar roles'), ('eliminar_roles', 'Puede eliminar roles')), 'verbose_name_plural': 'Rol'},
        ),
    ]
