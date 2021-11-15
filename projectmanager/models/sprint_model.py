from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission
from django.contrib.postgres.fields import ArrayField
from .proyecto_model import Proyecto


class Sprint(models.Model):
    """
    Spring: es un periodo de tiempo en el que se realizan una cantidad de userstoies

    Atributos:

    Parameters
    ----------

    estado
        Define el estado del sprint

    fecha_inicio
        fecha de inicio de spriot

    duracion_estiamda
        duracion estimada del Sprint

    fecha_finalizacion
        fecha en la que finalizara el sprint

    proyecto
        proyecto al cual esta ligado el sprint
    """
    ESTADOS = (
        ('conf1', 'Carga de Sprint Backlog'),
        ('conf2', 'Planning Poker'),
        ('conf3', 'Sprint en desarrollo'),
        ('fin', 'Sprint finalizado'),
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_inicio_desarrollo = models.DateTimeField(null=True, blank=True)
    duracion_estimada_dias = models.IntegerField(null=True, blank=True)
    duracion_restante_dias = models.IntegerField(blank=True, null=True)
    horas_realizadas = models.FloatField(null=True, blank=True, default=0)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion_real = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='conf1')
    proyecto = models.ForeignKey(Proyecto, related_name="registro_sprints", on_delete=models.CASCADE, null=True)
    proyecto_actual = models.OneToOneField(Proyecto, related_name="sprint_actual", blank=True, null=True,
                                           on_delete=models.CASCADE)
    proyecto_sig = models.OneToOneField(Proyecto, related_name="siguiente_sprint", blank=True, null=True,
                                        on_delete=models.CASCADE)
    saved_us_progress = ArrayField(models.IntegerField(), null=True, blank=True)
    saved_horas_us_total = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sprint'
        verbose_name_plural = 'Sprints'
