from django.db import models
from django.contrib.auth.models import User
from projectmanager.models import UserStory, Sprint


class CapacidadSMasteSprint(models.Model):
   """
   Guarda la capacidad de un desarrollador en un sprint
   """
   capacidad_horas = models.FloatField(blank=True, null=True)
   saldo_horas = models.FloatField(blank=True, null=True, default=capacidad_horas)

   sprint = models.ForeignKey(Sprint, related_name="capacidad_de_smembers", on_delete=models.CASCADE)
   scrum_member = models.ForeignKey(User, related_name="capacidad_sprints", on_delete=models.CASCADE)