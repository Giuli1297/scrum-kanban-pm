from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission
from .proyecto_model import Proyecto


class Rol(models.Model):
    """
    Modelo que hereda de Groups todos sus metodos y atributos para crear los roles y define los permisos para el CRUD

    Atributos:

    Parameters
    -----------

    descipcion
        descripcion del rol

    tipo
        define que tipo de rol es, ya sea de sistema, proyecto, por default o importado

    proyecto
        define a que proyecto corresponde el rol

    """
    TIPOS = (
        ('sistema', 'Rol de Sistema'),
        ('proyecto', 'Rol de Proyecto'),
        ('defecto', 'Roles por Defecto'),
        ('proyimp', 'Roles de Proyecto Importados')
    )

    related_group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="rol", primary_key=True,
                                         default=0)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=8, choices=TIPOS, default='sistema')
    proyecto = models.ForeignKey(Proyecto, related_name="roles", on_delete=models.CASCADE, blank=True, null=True)
    copied_from = models.CharField(max_length=255, blank=True, null=True)

    # Bueno Bro lo que tenes que hacer hoy es:
    #     8 - Importar y Exportar Roles
    class Meta:
        permissions = (('ver_roles', 'Puede ver roles'),
                       ('crear_roles', 'Puede crear roles'),
                       ('actualizar_roles', 'Puede actualizar roles'),
                       ('eliminar_roles', 'Puede eliminar roles'),
                       ('asignar_roles', 'Asigna roles a usuarios'),
                       ('quitar_roles', 'Quita rol de usuarios'))
        default_permissions = ()
        verbose_name_plural = 'Roles'

    def __str__(self):
        if self.proyecto:
            if self.descripcion:
                return self.related_group.name + ' - ' + self.proyecto.nombre + ' - ' + self.descripcion
            return self.related_group.name + ' - ' + self.proyecto.nombre
        else:
            return self.related_group.name
