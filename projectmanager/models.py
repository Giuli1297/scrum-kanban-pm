from django.contrib.auth.models import User ,AbstractUser,Group
from django.db import models
from django.urls import reverse


# Create your models here.
class Proyecto(models.Model):
    ESTADOS = (
        ('PEN', 'Pendiente'),
        ('CAN', 'Cancelado'),
        ('ACT', 'Activo'),
        ('FIN', 'Finalizado')
    )

    nombre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=3, choices=ESTADOS)
    scrum_master = models.ForeignKey(User, related_name='proyecto_encargado', on_delete=models.CASCADE)
    scrum_member = models.ManyToManyField(User, related_name='proyecto_asignado')
    # Cambiar luego a manytomany de userstories
    product_backlog = models.TextField(blank=True)
    # Cambiar luego a manytomany de sprints
    sprintList = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Proyectos'
        permissions = (('can_create', 'Puede crear un proyecto'),)
        ordering = ('-fecha_inicio',)

    def get_absolute_url(self):
        return reverse('proyecto_detail', args=[self.slug])

    def __str__(self):
        return self.nombre


class rol(Group):
    usuario=models.ManyToManyField(User)
    class Meta:
        verbose_name_plural='Rol'
        ordering=['name']
    def __unicode__(self):
        return self.name