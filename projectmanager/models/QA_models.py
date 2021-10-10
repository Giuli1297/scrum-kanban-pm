from django.db import models
from django.contrib.auth.models import User
from projectmanager.models import UserStory


class QA(models.Model):
    user_story = models.OneToOneField(UserStory, related_name='QA', on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(max_length=255)
    aceptar = models.BooleanField(default=False)
