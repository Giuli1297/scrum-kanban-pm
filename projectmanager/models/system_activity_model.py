from django.db import models
from django.contrib.auth.models import User


class SystemActivity(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, related_name="actividad", on_delete=models.CASCADE)
    descripcion = models.TextField(max_length=255)
