from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator,MaxValueValidator
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

    class Meta:
        verbose_name = 'Proyectos'
        permissions = (('crear_proyecto', 'Puede crear un proyecto'),
                       ('editar_proyecto', 'Puede editar un proyecto'),
                       ('ver_proyecto', 'Puede ver un proyecto en detalle'),
                       ('ver_proyectos', 'Puede ver proyectos'),
                       ('cancelar_proyecto', 'Puede cancelar un proyecto en estado pendiente'),
                       ('gestionar_scrum_members', 'Puede Agregar/Quitar Scrum Members de un proyecto'),
                       ('iniciar_proyecto', 'Puede iniciar proyecto'),


                       ('crear_roles_proyecto', 'Puede Crear Roles de Proyecto'),
                       ('ver_roles_proyecto', 'Puede ver roles de proyecto'),
                       ('modificar_roles_proyecto', 'Puede Modificar Roles de Proyecto'),
                       ('eliminar_roles_proyecto', 'Puede eliminar roles de proyecto'),
                       ('ver_users_storys', 'Puede ver user storys'),
                       ('crear_users_storys', 'Puede crear users storys'),
                       ('actualizar_users_storys', 'Puede actualizar users storys'),
                       ('eliminar_users_storys', 'Puede ver users storys'),
                       ('puede_asignar_users_storys', 'Asigna roles a usuarios'),
                       ('puede_quitar_users_storys', 'Quita users storys de usuarios'),
                       ('gestionar_roles_proyecto', 'Puede Agregar/Asignar/Modificar/Eliminar Roles de un Proyecto'),
                       ('importar_roles_proyecto', 'Puede Importar roles de proyecto'),
                       ('gestionar_user_stories', 'Puede Agregar/Modificar/Eliminar User Stories de un proyecto'),)


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



class Sprint(models.Model):
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    duracion_estimada = models.IntegerField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    proyecto = models.ForeignKey(Proyecto, related_name="registro_sprints", on_delete=models.CASCADE)
    proyecto_actual = models.OneToOneField(Proyecto, related_name="sprint_actual", blank=True, null=True,
                                           on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'




class UserStory(models.Model):
    ESTADOS = (
        ('Nuevo', 'Nuevo'),
        ('Cancelado', 'Cancelado'),
        ('To-Do', 'To-Do'),
        ('Doing', 'Doing'),
        ('Done', 'Done'),
        ('QA', 'QA'),
        ('Release', 'Release')
    )
    descripcion=models.TextField(blank=True,max_length=255)
    tiempoEstimado=models.IntegerField(validators=[MinValueValidator(0)],default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Nuevo')
    tiempoEnDesarrollo=models.IntegerField(validators=[MinValueValidator(0)],default=0)
    desarrolladorAsignado=models.ForeignKey(User,related_name='desarrollador_asignado',null=True, on_delete=models.CASCADE)
    proyecto=models.ForeignKey(Proyecto,related_name='product_backlog',null=True,on_delete=models.CASCADE)
    sprint=models.ForeignKey(Sprint,related_name='sprint_backlog',null=True,blank=True,on_delete=models.SET_NULL)
    prioridad=models.IntegerField(default=1)
    def historial(self):
        return HistorialUs.objects.filter(descripcion=self).order_by('version')

    class Meta:
        verbose_name='User Story'
        verbose_name_plural = 'Users Storys'
        ordering=['-prioridad']
    def __str__(self):
        return self.descripcion

class HistorialUs(models.Model):
    version=models.IntegerField(editable=False)
    ESTADOS = (
        ('Nuevo', 'Nuevo'),
        ('Cancelado', 'Cancelado'),
        ('To-Do', 'To-Do'),
        ('Doing', 'Doing'),
        ('Done', 'Done'),
        ('QA', 'QA'),
        ('Release', 'Release')
    )
    us=models.ForeignKey(UserStory,related_name='UsHistorial',null=True,on_delete=models.CASCADE)
    descripcion=models.TextField(blank=True,max_length=255)


    class Meta:
        unique_together=('version','us')
    def save(self, *args, **kwargs):
        cont_version=HistorialUs.objects.filter(us=self.us).order_by('-version')[:1]
        self.version=cont_version[0].version + 1 if cont_version else 1
        super(HistorialUs, self).save(*args,**kwargs)
class UserInfo(models.Model):
    """
    Modelo que guarda informacion util sobre cada usuario del sistema
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info', primary_key=True)
    horasDisponibles = models.PositiveIntegerField(default=40)


