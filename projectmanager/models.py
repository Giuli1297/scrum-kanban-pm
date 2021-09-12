from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission


def get_name(self):
    return self.name


Permission.add_to_class("__str__", get_name)


# Create your models here.
class Proyecto(models.Model):
    """
        Guarda y define los campos del proyecto

        Atributos:

        Parameters
        ----------
        estado
            Define el estado del proyecto, ya sea pendiente, cancelado, activo, finalizado

        nombre
            Define el nombre de proyecto

        descripcion
            Breve descripcion del proyecto

        Fecha_inicio
            Establece la fecha de inicio del proyecto

        Fecha_fin
            Fecha del final del proyectos

        scrum_master
            Encargado del equipo del proyecto

        scrum_member
            Lista de miembros del equipo

        """
    ESTADOS = (
        ('PEN', 'Pendiente'),
        ('CAN', 'Cancelado'),
        ('ACT', 'Activo'),
        ('FIN', 'Finalizado')
    )

    nombre = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=3, choices=ESTADOS, default='PEN')
    scrum_master = models.ForeignKey(User, related_name='proyecto_encargado', on_delete=models.CASCADE)
    scrum_member = models.ManyToManyField(User, related_name='proyecto_asignado', blank=True)
    # Cambiar luego a manytomany de userstories
    product_backlog = models.TextField(blank=True)
    # Cambiar luego a manytomany de sprints
    sprintList = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Proyectos'
        permissions = (('crear_proyecto', 'Puede crear un proyecto'),
                       ('editar_proyecto', 'Puede editar un proyecto'),
                       ('ver_proyecto', 'Puede ver un proyecto en detalle'),
                       ('ver_proyectos', 'Puede ver proyectos'),
                       ('iniciar_proyecto', 'Puede iniciar proyecto'),
                       ('crear_roles_proyecto', 'Puede Crear Roles de Proyecto'),
                       ('ver_roles_proyecto', 'Puede ver roles de proyecto'),
                       ('modificar_roles_proyecto', 'Puede Modificar Roles de Proyecto'),
                       ('eliminar_roles_proyecto', 'Puede eliminar roles de proyecto'))
        default_permissions = ()
        ordering = ('-fecha_inicio',)

    def save(self, *args, **kwargs):
        """
        Guarde la instancia actual. Reemplace esto en una subclase si desea controlar el proceso de guardado.

        """
        self.nombre = self.nombre.lower()
        if not self.slug:
            self.slug = slugify(self.nombre)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('proyecto_detail', args=[self.slug])

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """
    Modelo que hereda de Groups todos sus metodos y atributos para crear los roles y define los permisos para el CRUD
    """
    TIPOS = (
        ('sistema', 'Rol de Sistema'),
        ('proyecto', 'Rol de Proyecto')
    )

    related_group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="rol", primary_key=True)
    tipo = models.CharField(max_length=8, choices=TIPOS, default='sistema')
    proyecto = models.ForeignKey(Proyecto, related_name="roles", on_delete=models.CASCADE, blank=True, null=True)

    # Bueno Bro lo que tenes que hacer hoy es:
    #     1 - Hacer que se cree una entidad rol cuando se crea un grupo
    #     2 - Que se defina el tipo de rol que se crea
    #     3 - Que si se crea un rol nivel proyecto se linkee al proyecto (podria se m2m en vez de o2m)
    #     4 - Completar CRUD de rol nivel proyecto
    #     5 - Pantalla de Asinar rol nivel proyecto
    #     6 - Que liste solo roles del proyecto actual
    #     7 - Que liste solo roles de sistema en roles de sistema crud
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
        return self.related_group.name
