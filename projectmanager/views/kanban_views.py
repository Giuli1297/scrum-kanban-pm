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


class SeleccionarParaRealizarUserStory(View):
    """
    Vista basada en clase que sirve para cargar el sprint backlog
    """

    def get(self, request, usPk, *args, **kwargs):
        user_story = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      user_story) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        user_story.estado = 'Doing'
        user_story.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha seleccionado el user story " + str(user_story.pk)
                                                  + " para desarrollarlo")
        messages.success(request, 'User Story agregado a doing')
        return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
