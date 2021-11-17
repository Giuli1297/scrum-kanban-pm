from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from projectmanager.models import UserStory


class QA(models.Model):
    """
        Guarda y define los campos del quality assurance

        Atributos:

        Parameters
        ----------
        user story
            User Story a ser verificado

        fecha
            fecha en la que se realiza el control de calidad.

        comentario
            Comentario referente a alguna observacion.

        aceptar
            Valor booleano que defino si el user story es aprobado o no.
    """
    user_story = models.OneToOneField(UserStory, related_name='QA', on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    comentario = models.TextField(max_length=255)
    aceptar = models.BooleanField(default=False)
