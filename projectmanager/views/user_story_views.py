from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.db.models import Q
import logging
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    TemplateView,
    DetailView
)
from scrum_kanban_pm.settings.development import EMAIL_HOST_USER
from projectmanager.forms import *
from django.core.mail import EmailMessage
from projectmanager.forms import UserForm, RolForm, UserFormDelete
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from projectmanager.utils import account_activation_token, add_user_to_obj_group, add_perm_to_group, \
    add_obj_perm_to_group, \
    add_users_to_obj_group, remove_all_perms_from_obj_group, remove_all_users_from_obj_group
from guardian.shortcuts import get_perms
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
# Create your views here.
from projectmanager.models import *

from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.sites.shortcuts import get_current_site
from projectmanager.views.general_views import UserAccessMixin


class UserStoryCreate(View):
    """
    Vista para crear y listar User Storys

    US
        obtiene todos los USER STORYS en el metodo get y lista los USER STORYS
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US = UserStory.objects.filter(proyecto=proyecto)
        form = ProyectoUs()
        context = {
            'form': form,
            'proyecto': proyecto,
            'US': US
        }
        return render(request, 'UserStory/crearUS.html', context)

    def post(self, request, slug, *args, **kwargs):
        """
        Se obtiene el proyecto en el que se está trabajando y se crea una instancia de USER STORY y se le asigna los datos correspondientes del form y tambien el proyecto
        al cual pertenece
        """
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        form = ProyectoUs(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripción_de_user_story']
            prioridad = form.cleaned_data['prioridad_1_al_10']
            if prioridad > 0 and prioridad < 11:
                US = UserStory.objects.create(descripcion=descripcion, proyecto=proyecto, prioridad=prioridad)
                US.save()
                # Log activity
                SystemActivity.objects.create(usuario=request.user,
                                              descripcion="Ha creado un user story en el proyecto " + proyecto.nombre)
                messages.success(request, "User Story Creado Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class UserStoryUpdate(View):
    """
        Vista para actualizar los datos de descripcion y prioridad de un User Story

        US
            obtiene el user story con metodo get y su pk

    """

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
        if US2.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        form = ProyectoUs(initial={
            'descripción_de_user_story': US2.descripcion,
            'prioridad_1_al_10': US2.prioridad
        })
        context = {
            'form': form,
            'proyecto': proyecto,
            'US2': US2
        }
        return render(request, 'UserStory/UpdateUs.html', context)

    def post(self, request, slug, pk, *args, **kwargs):
        """
        Se obtiene el objeto del User Story actual y se actualiza
        con los nuevos datos de entrada
        """
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
        if US2.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        form = ProyectoUs(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripción_de_user_story']
            prioridad = form.cleaned_data['prioridad_1_al_10']
            if prioridad > 0 and prioridad < 11:
                nuevoHistorial = HistorialUs(us=US2, descripcion=US2.descripcion)
                nuevoHistorial.save()
                US2.descripcion = descripcion
                US2.prioridad = prioridad

                US2.save()
                # Log activity
                SystemActivity.objects.create(usuario=request.user,
                                              descripcion="Ha modificado un user story en el proyecto " + proyecto.nombre)
                messages.success(request, "User Story se actualizó Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")

        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class EliminarUs(View):
    """
    Clase para eliminar un user story
    Se obtiene el objeto por su pk y se hace un delete
    """

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US = UserStory.objects.get(pk=pk)
        if US.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        US.delete()
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha eliminado un user story en el proyecto " + proyecto.nombre)
        messages.success(request, "User Story Eliminado")
        return redirect('create_us', slug=slug)
