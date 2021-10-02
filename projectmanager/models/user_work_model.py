from django.contrib.auth.models import User, AbstractUser, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Permission
from .proyecto_model import Proyecto


class UserWorkTime(models.Model):
    """
    Modelo que sirve para administrar las horas de trabajo de un usuario

    Atributos:

    Parameters
    -----------

    dias_laborales
        dias laborales, lunes a viernes



    """
    DIAS_LABORALES = (
        ('LUN', 'LUNES'),
        ('MAR', 'MARTES'),
        ('MIE', 'MIERCOLES'),
        ('JUE', 'JUEVES'),
        ('VIE', 'VIERNES'),
    )

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='tiempos_de_usuarios')
    desarrollador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tiempos_de_trabajo')
    dia = models.CharField(max_length=20, choices=DIAS_LABORALES)
    horas = models.FloatField(default=0.0)
    totalEnProyecto = models.FloatField(blank=True, null=True)
