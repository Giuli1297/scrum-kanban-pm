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
from django.http import JsonResponse
import json


class CrearRolProyecto(UserAccessMixin, View):
    """
        Vista basada en clase el sirve para crear un rol a nivel proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        form = CrearRolProyectoForm(slug=slug)
        context = {
            'form': form,
            'proyecto': proyecto
        }
        return render(request, 'rol_proyecto/crear_rol.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        form = CrearRolProyectoForm(request.POST, slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            permissions = form.cleaned_data['permisos']
            usuarios_a_asignar = form.cleaned_data['scrum_members']
            for permiso in permissions:
                group = add_obj_perm_to_group(nombre, permiso.codename, proyecto)
            for user in usuarios_a_asignar:
                add_user_to_obj_group(user, nombre)
            rol = Rol.objects.get(related_group=group)
            rol.descripcion = descripcion
            rol.save()

            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha creado un rol nivel proyecto en el proyecto "
                                                      + proyecto.nombre + " con el nombre " + nombre)

            messages.success(request, "Rol Creado Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('proyecto_rol', slug=slug)


class ModificarRolProyecto(UserAccessMixin, View):
    """
    Vista basada en clase el sirve para modificar un rol a nivel proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        rol = Rol.objects.get(pk=pk)
        perm_names = get_perms(rol.related_group, proyecto)
        permisos = []
        for perm_name in perm_names:
            permisos.append(Permission.objects.filter(codename=perm_name)[0])
        form = CrearRolProyectoForm(
            initial={'nombre': rol.related_group.name,
                     'descripcion': rol.descripcion,
                     'permisos': permisos,
                     'scrum_members': rol.related_group.user_set.all()}, slug=slug)
        context = {
            'form': form,
            'proyecto': proyecto,
            'rol': rol
        }
        return render(request, 'rol_proyecto/modificar_rol.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        form = CrearRolProyectoForm(request.POST, slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            permissions = form.cleaned_data['permisos']
            usuarios_a_asignar = form.cleaned_data['scrum_members']
            remove_all_perms_from_obj_group(nombre, proyecto)
            remove_all_users_from_obj_group(nombre)
            for permiso in permissions:
                add_obj_perm_to_group(nombre, permiso.codename, proyecto)
            for user in usuarios_a_asignar:
                add_user_to_obj_group(user, nombre)

            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha modificado el rol " + nombre
                                                      + " del proyecto " + proyecto.nombre)

            messages.success(request, "Rol Modificado Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('proyecto_rol', slug)


class EliminarRolProyecto(UserAccessMixin, View):
    """
    Vista basada en clase el sirve para eliminar un rol a nivel proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)

        rol = Rol.objects.get(pk=pk)
        if rol.tipo == 'defecto':
            messages.error(request, "Este Rol es defecto")
            return redirect('proyecto_rol', slug=slug)
        related_group = rol.related_group
        related_group.delete()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha eliminado el rol " + rol.related_group.name
                                                  + "del proyecto " + proyecto.nombre)

        messages.success(request, "Rol Eliminado")
        return redirect('proyecto_rol', slug)


class ImportarRolProyecto(UserAccessMixin, View):
    """
    Vista basada en clase el sirve para eliminar un rol a nivel proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.importar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        roles = Rol.objects.filter(~Q(proyecto=proyecto) & ~Q(tipo='defecto'))
        form = ImportarRolProyectoForm(slug=slug)
        context = {
            'proyecto': proyecto,
            'roles': roles,
            'form': form
        }
        return render(request, 'rol_proyecto/importar_rol.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.importar_roles_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        form = ImportarRolProyectoForm(request.POST, slug=slug)
        if form.is_valid():
            roles = form.cleaned_data['roles']
            for rol in roles:
                print('xd1')
                perm_names = get_perms(rol.related_group, rol.proyecto)
                for permiso in perm_names:
                    print('xd')
                    add_obj_perm_to_group(rol.related_group.name + '_' + proyecto.slug, permiso,
                                          proyecto)
                group = Group.objects.get(name=rol.related_group.name + '_' + proyecto.slug)
                created_rol = Rol.objects.get(related_group=group)
                created_rol.descripcion = rol.descripcion
                created_rol.tipo = 'proyimp'
                created_rol.copied_from = rol.related_group.name
                created_rol.save()
                # Log activity
                SystemActivity.objects.create(usuario=request.user,
                                              descripcion="Ha importado el rol" + rol.related_group.name + " en el proyecto"
                                                          + proyecto.nombre)
            messages.success(request, "Roles Importados Correctamente!")
        return redirect('proyecto_rol', slug=slug)


def get_list_users_group(request):
    if request.method == "POST":
        body = json.loads(request.body)
        users = User.objects.filter(groups=body["data"])
        user_list = []
        for user in users:
            user_list.append(user.username);
        return JsonResponse({"status": 200, "usuarios": user_list})
    return JsonResponse({"status": 400})
