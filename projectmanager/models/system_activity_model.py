from django.db import models
from django.contrib.auth.models import User


class SystemActivity(models.Model):
    """
            Guarda y define los cambios y actividades del sistema

            Atributos:

            Parameters
            ----------
            fecha
                fecha en la cual el cambio o actividad fue realizado

            usuario
                usuario que realiza el cambio o actividad.

            descripcion
                descripcion breve del cambio o actividad realizada.
    """
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, related_name="actividad", on_delete=models.CASCADE)
    descripcion = models.TextField(max_length=255)
