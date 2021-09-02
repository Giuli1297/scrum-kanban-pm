from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify
from guardian.shortcuts import assign_perm


# Create your models here.
class Proyecto(models.Model):
    """
    Guarda y define los campos de un proyecto.
    ...

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
    # Cambiar luego a manytomany de userstories
    product_backlog = models.TextField(blank=True)
    # Cambiar luego a manytomany de sprints
    sprintList = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Proyectos'
        permissions = (('crear_proyecto', 'Puede crear un proyecto'),
                       ('editar_proyecto', 'Puede editar un proyecto'),
                       ('ver_proyecto', 'Puede ver un proyecto en detalle'),
                       ('ver_proyectos', 'Puede ver proyectos'),
                       ('iniciar_proyecto', 'Puede iniciar proyecto'),)
        ordering = ('-fecha_inicio',)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('proyecto_detail', args=[self.slug])

    def __str__(self):
        return self.nombre
