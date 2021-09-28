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


class RolListView(UserAccessMixin, ListView):
    """
    Vista basada en clase que muestra una lista delos roles
    Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Rol

    """
    raise_exception = False
    permission_required = ('projectmanager.ver_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Group
    queryset = Group.objects.filter(Q(rol__tipo='sistema'))
    template_name = 'rol/list.html'


class RolCreateView(UserAccessMixin, CreateView):
    """
       Vista basada en clase para poder crear los roles
       Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Group

        formclass
            El formulario a utilizar es el del Rol
    """
    raise_exception = False
    permission_required = ('projectmanager.crear_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = Group
    form_class = RolForm
    template_name = 'rol/create.html'
    success_url = reverse_lazy('list_rol')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        returnValue = super().form_valid(form)
        Rol.objects.create(related_group=self.object, tipo='sistema')
        return returnValue


class RolUpdateView(UserAccessMixin, UpdateView):
    """
      Vista basada en clase para poder modificar un rol
      Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Group

        formclass
            El formulario a utilizar es el del Rol
    """
    raise_exception = False
    permission_required = ('projectmanager.actualizar_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = Group
    form_class = RolForm
    template_name = 'rol/update.html'
    success_url = reverse_lazy('list_rol')


class RolDeleteView(UserAccessMixin, DeleteView):
    """
      Vista basada en clase para poder eliminar rol
      Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Group
    """
    raise_exception = False
    permission_required = ('projectmanager.eliminar_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = Group
    template_name = 'rol/delete.html'
    success_url = reverse_lazy('list_rol')


class ListUser(ListView):
    """
      Vista basada en clase que muestra una lista de los usuarios
      Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de User

    """
    model = User
    # form_class = UserForm
    template_name = 'rol/list_user.html'


class AsignarRol(UserAccessMixin, UpdateView):
    """
      Vista basada en clase para poder asignar un rol a un usuario
      Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de User

        formclass
            El formulario a utilizar es el del User
    """
    raise_exception = False
    permission_required = ('projectmanager.asignar_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = User
    form_class = UserForm
    template_name = 'rol/asignarRol.html'
    success_url = reverse_lazy('list_user')


class EliminarRolUser(UserAccessMixin, UpdateView):
    """
          Vista basada en clase para poder eliminar rol a un usuario
          Atributos:

            Parameters
            ----------
            model
                Modelo a utilizar seria el de User
            form_class
                El formulario a utilizar es del UserFormDelete
        """
    raise_exception = False
    permission_required = ('projectmanager.quitar_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = User
    form_class = UserFormDelete
    template_name = 'rol/eliminarRolUser.html'
    success_url = reverse_lazy('list_user')
