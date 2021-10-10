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


class UserAccessMixin(PermissionRequiredMixin):
    """
        Clase donde esta centralizada la verificacion de los permisos
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(),
                                     self.get_login_url(), self.get_redirect_field_name())
        if not self.has_permission():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)


class VerificationView(View):
    """
        Vista que verifica si el usuario ya fue habilitado por el administrador
    """

    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                messages.error(request, "El usuario no pudo ser habilitado2")
                return redirect('home')

            if user.is_active:
                messages.error(request, "El usuario no pudo ser habilitado1")
                return redirect('home')
            user.is_active = True
            user.save()
            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Se ha verificado al usuario " + user.username)

            messages.success(request, "Usuario " + user.username + " habilitado")
            return redirect('home')
        except Exception as ex:
            messages.error(request, "El usuario no pudo ser habilitado")
            return redirect('home')


class HomePage(LoginRequiredMixin, TemplateView):
    """
    Devuelve la pagina principal de la aplicacion

    Parameters
    ----------
    request
        Objeto que contiene info acerca de la solicitud del cliente

    """
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SystemActivityView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('home')
        return render(request, 'dashboard/system_activity.html', context={
            'registro': SystemActivity.objects.all().order_by('-fecha')
        })
