from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission
from .sprint_model import Sprint
from .proyecto_model import Proyecto


class UserStory(models.Model):
    """
    Clase que representa a los USerStory

    Atributos:

    Parameters
    -----------
    estado
        Define el estado del UserStory

    nombre
        Define el nombre del UserStory

    descripcion
        Breve descripcion del UserStory

    tiempoEstimadoSMaster
        tiempo estimado por el scrum master

    tiempoEnDesarrollo
        tiempo que lleva en desarrollo el userstory

    tiempoEstimado
        tiempo estimado para realizar el UserStory

    desarrolladorAsignado
        desarrollador asignado para realizar el UserStory

    saldos_horas
        El saldo de hora del sprint

    proyecto
        Proyecto al cual esta ligado el UserStory

    Sprint
        Sprint en donde esta contenido el UserStory

    priodidad
        priodidad asignada al userstory
    """
    ESTADOS = (
        ('Nuevo', 'Nuevo'),
        ('no-terminado', 'No Terminado'),
        ('To-Do', 'To-Do'),
        ('Doing', 'Doing'),
        ('Done', 'Done'),
        ('QA', 'QA'),
        ('Release', 'Release')
    )
    descripcion = models.TextField(blank=True, max_length=255)
    tiempoEstimadoSMaster = models.FloatField(default=0.0)
    tiempoEstimado = models.FloatField(validators=[MinValueValidator(0)], default=0, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Nuevo')

    tiempoEnDesarrollo = models.FloatField(validators=[MinValueValidator(0)], default=0, null=True)
    saldo_horas = models.FloatField(default=0.0)
    desarrolladorAsignado = models.ForeignKey(User, related_name='desarrollador_asignado', null=True, blank=True,
                                              on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, related_name='product_backlog', null=True, on_delete=models.CASCADE)
    sprint = models.ForeignKey(Sprint, related_name='sprint_backlog', null=True, blank=True, on_delete=models.SET_NULL)
    prioridad = models.IntegerField(default=1)
    descripcionDone = models.TextField(blank=True, max_length=255)

    def historial(self):
        return HistorialUs.objects.filter(descripcion=self).order_by('version')

    def save(self, *args, **kwargs):
        self.saldo_horas = self.tiempoEstimado - self.tiempoEnDesarrollo
        super().save(*args, **kwargs)

    class Meta:
        permissions = (
            ('desarrollar_user_story', 'Puede desarrollar un user story'),)
        verbose_name = 'User Story'
        verbose_name_plural = 'Users Storys'
        ordering = ['estado', '-prioridad']

    def __str__(self):
        return self.descripcion + self.proyecto.slug


class logHistorial(models.Model):
    """
        Guarda y define el registro de las actividades realizadas en el user story

        Atributos:

        Parameters
        ----------
        us
            identificador del user story

        fecha
            fecha en la que se realizo el cambio

        descripcion
            descripcion breve del cambio realizado.

        usuaria
            usuario que realiza el cambio
        """
    us = models.ForeignKey(UserStory, related_name='logHistorial', null=True, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, max_length=255)
    fecha=models.DateTimeField(auto_now_add=True)
    usuario=models.ForeignKey(User,null=True,on_delete=models.CASCADE)




class HistorialUs(models.Model):
    """
        Guarda y define el registro de las actividades realizadas en el user story

        Atributos:

        Parameters
        ----------
        us
            identificador del user story

        fecha
            fecha en la que se realizo el cambio

        descripcion
            descripcion breve del cambio realizado.

        usuaria
            usuario que realiza el cambio
        """
    version = models.IntegerField(editable=False)
    us = models.ForeignKey(UserStory, related_name='UsHistorial', null=True, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, max_length=255)
    fecha=models.DateTimeField(default=timezone.now)
    usuario=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    descripcionDone = models.TextField(blank=True, max_length=255)
    prioridad=models.IntegerField(blank=True,default=0)
    idUs = models.IntegerField(blank=True,default=0)

    class Meta:
        unique_together = ('version', 'us')

    def save(self, *args, **kwargs):
        """
            Guarde la instancia actual. Reemplace esto en una subclase si desea controlar el proceso de guardado.

        """
        cont_version = HistorialUs.objects.filter(us=self.us).order_by('-version')[:1]
        self.version = cont_version[0].version + 1 if cont_version else 1
        super(HistorialUs, self).save(*args, **kwargs)


class UserInfo(models.Model):
    """
    Modelo que guarda informacion util sobre cada usuario del sistema
    Atributos:

        Parameters
        ----------
        usuario
            identificador de usuario

        horasisponibles
            horas disponibles del usuario.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='info', primary_key=True)
    horasDisponibles = models.FloatField(default=40.0)


class RegistroActividadDiairia(models.Model):
    """
        Guarda y define el registro de las actividades realizadas diariamente

        Atributos:

        Parameters
        ----------
        us
            identificador del user story

        hora
            hora en la que se realizo el cambio

        descripcion
            descripcion breve del cambio realizado.
    """
    us = models.ForeignKey(UserStory, related_name='RegistroActividad', null=True, on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True, max_length=5000)
    fecha = models.DateTimeField(default=timezone.now)
    hora = models.FloatField(default=0)
