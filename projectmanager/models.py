from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings 

# Create your models here.
class Proyecto(models.Model):

    nombre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=10)
    scrum_master = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='proyecto_encargado', on_delete=models.CASCADE)
    scrum_member = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='proyecto_asignado')
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



class CuentaPersonalizada(BaseUserManager):

    def create_superuser(self, email, nombre, apellido, password, **otros_campos):
    
        otros_campos.setdefault('is_staff', True)
        otros_campos.setdefault('is_superuser', True)
        otros_campos.setdefault('is_active', True)

        if otros_campos.get('is_staff') is not True:
            raise ValueError(
                'Superuser debe asignar el campo is_staff=True.')
        if otros_campos.get('is_superuser') is not True:
            raise ValueError(
                'Superuser debe asignar el campo is_superuser=True.')
        return self.create_user(email, nombre, apellido, password, **otros_campos)

    def create_user(self, email, nombre, apellido, password, **otros_campos):
    
        if not email:
            raise ValueError('El email es requerido')

        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre,
                          apellido=apellido, **otros_campos)
        user.set_password(password)
        user.save()
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    identificador = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100) 
    fecha_creacion = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CuentaPersonalizada()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["nombre", "apellido"] 

    def __str__(self):
        return self.email 


