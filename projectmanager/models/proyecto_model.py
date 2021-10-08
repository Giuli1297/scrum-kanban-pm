from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission


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

    class Meta:
        verbose_name = 'Proyectos'
        permissions = (('crear_proyecto', 'Puede crear un proyecto'),
                       ('editar_proyecto', 'Puede editar un proyecto'),
                       ('ver_proyecto', 'Puede ver un proyecto en detalle'),
                       ('ver_proyectos', 'Puede ver proyectos'),
                       ('cancelar_proyecto', 'Puede cancelar un proyecto en estado pendiente'),
                       ('gestionar_scrum_members', 'Puede Agregar/Quitar Scrum Members de un proyecto'),
                       ('iniciar_proyecto', 'Puede iniciar proyecto'),
                       ('gestionar_roles_proyecto', 'Puede Agregar/Asignar/Modificar/Eliminar Roles de un Proyecto'),
                       ('importar_roles_proyecto', 'Puede Importar roles de proyecto'),
                       ('gestionar_user_stories', 'Puede Agregar/Modificar/Eliminar User Stories de un proyecto'),
                       ('iniciar_ppoker_proyecto', 'Puede iniciar planning poker de un sprint'),
                       ('estimar_userstory_proyecto', 'Puede estimar User Stories en el Sprint Backlog'),
                       ('cargar_sprint_backlog_proyecto', 'Puede cargar User Stories en el Sprint Backlog'),
                       ('estimar_sprint', 'Puede estimar sprint'),
                       ('realizar_qa', 'Puede realizar QA a user stories'))
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
