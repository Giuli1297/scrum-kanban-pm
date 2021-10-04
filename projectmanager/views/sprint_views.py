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
from django.urls import reverse_lazy, reverse
from django.contrib.sites.shortcuts import get_current_site
from projectmanager.views.general_views import UserAccessMixin


class CargarSprintBacklog(View):
    """
    Vista basada en clase que sirve para cargar el sprint backlog
    """

    def get(self, request, usPk, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      sprint.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=sprint.proyecto.slug)
        if sprint.estado != 'conf1':
            messages.error(request, "Ya no puedes agregar user stories al sprint backlog")
            return redirect('proyecto_gestion', slug=sprint.proyecto.slug)
        ustory = UserStory.objects.get(pk=usPk)
        ustory.sprint = sprint
        ustory.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha agregado el user story con id " + ustory.pk
                                                  + " al sprint backlog del proyecto " + sprint.proyecto_actual.nombre)
        messages.success(request, 'User Story agregado al SprintBacklog')
        return redirect('proyecto_gestion', slug=sprint.proyecto_actual.slug)


class QuitarUSFromSprintBacklog(View):
    """
    Vista basada en clase utilizada para quitar un User Story del sprint backlog
    """

    def get(self, request, usPk, *args, **kwargs):
        ustory = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      ustory.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)
        ustory.sprint = None
        ustory.desarrolladorAsignado = None
        ustory.tiempoEstimado = 0
        ustory.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha removido el user story con id " + ustory.pk
                                                  + " del sprint backlog del proyecto " + ustory.proyecto.nombre)
        messages.success(request, 'User Story removido del SprintBacklog')
        return redirect('proyecto_gestion', slug=ustory.proyecto.slug)


class AsignarYEstimarUserStoryView(View):
    """
    Vista basada en clases para estimar y asignar user story
    """

    def get(self, request, usPk, *args, **kwargs):
        ustory = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.estimar_userstory_proyecto',),
                                      ustory.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)
        form = AsignarYEstimarUserStoryForm(usPk=usPk, initial={
            'horas_estimadas': ustory.tiempoEstimado,
            'scrum_member_asignado': ustory.desarrolladorAsignado
        })
        context = {
            'ustory': ustory,
            'form': form
        }
        return render(request, 'sprint/estimar_us_sm.html', context)

    def post(self, request, usPk, *args, **kwargs):
        ustory = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.estimar_userstory_proyecto',),
                                      ustory.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)
        form = AsignarYEstimarUserStoryForm(request.POST, usPk=usPk)
        if form.is_valid():
            horasEstimadas = form.cleaned_data['horas_estimadas']
            sm_asignado = form.cleaned_data['scrum_member_asignado']
            ustory.desarrolladorAsignado = sm_asignado
            ustory.tiempoEstimadoSMaster = horasEstimadas
            ustory.save()
        else:
            messages.error(request, "Un error a ocurrido")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha asginado y estimado el user story con id " + ustory.pk
                                                  + " del sprint backlog del proyecto " + ustory.proyecto.nombre)
        messages.success(request, "Se ha asignado y estimado el User Story")
        return redirect('proyecto_gestion', slug=ustory.proyecto.slug)


class PlanningPokerView(View):
    """
    Vista basada en clase para la gestion de planning poker
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.iniciar_ppoker_proyecto',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        if not proyecto.sprint_actual.sprint_backlog.exists():
            messages.error(request, 'No tienes user stories!')
            return redirect('proyecto_gestion', slug=proyecto.slug)
        if proyecto.sprint_actual.estado != 'conf1':
            messages.error(request, 'No se puede realizar planning poker')
            return redirect('proyecto_gestion', slug=proyecto.slug)
        for us in proyecto.sprint_actual.sprint_backlog.all():
            if not us.desarrolladorAsignado != None:
                messages.error(request, "Debes asignar todos los User Stories")
                return redirect('proyecto_gestion', slug=slug)
        proyecto.sprint_actual.estado = 'conf2'
        proyecto.sprint_actual.save()
        for us in proyecto.sprint_actual.sprint_backlog.all():
            current_site = get_current_site(request)
            email_body = {
                'user': us.desarrolladorAsignado,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(us.desarrolladorAsignado.pk)),
                'token': account_activation_token.make_token(us.desarrolladorAsignado),
                'usPk': us.pk
            }

            link = reverse('planning_poker_smember', kwargs={
                'uidb64': email_body['uid'], 'token': email_body['token'], 'usPk': email_body['usPk']})

            email_subject = 'Planning Poker User Storie: ' + us.descripcion

            activate_url = 'http://' + current_site.domain + link

            email = EmailMessage(
                email_subject,
                'Realize su estimacions del user story: ' + activate_url,
                EMAIL_HOST_USER,
                [us.desarrolladorAsignado.email],
            )
            email.send(fail_silently=False)
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha iniciado el planning poker en el proyecto " + proyecto.nombre)
        return redirect('proyecto_gestion', slug=proyecto.slug)


class PlanningPokerSMemberView(View):
    """
    Vista basada en clases pra la visualizacion de miembros del planning poker
    """

    def get(self, request, uidb64, token, usPk, *args, **kwargs):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                messages.error(request, "Token incorrecto")
                return redirect('home')

            ustory = UserStory.objects.get(pk=usPk)
            if ustory.tiempoEstimado != 0:
                messages.error(request, 'Este User Story ya a sido estimado')
                return redirect('home')
            form = PlanningPokerSMemberForm()
            context = {
                'user_story': ustory,
                'form': form
            }
            return render(request, 'sprint/planning_poker_scrummember.html', context)
        except Exception as ex:
            messages.error(request, "Error de Token")
            return redirect('home')

    def post(self, request, uidb64, token, usPk, *args, **kwargs):

        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                messages.error(request, "Token incorrecto")
                return redirect('home')

            user_story = UserStory.objects.get(pk=usPk)

            if user_story.tiempoEstimado != 0:
                messages.error(request, 'Este User Story ya a sido estimado')
                return redirect('home')

            form = PlanningPokerSMemberForm(request.POST)
            if form.is_valid():
                horas_estimadas_smember = float(form.cleaned_data['horas_estimadas'])
                horas_estimadas_smaster = float(user_story.tiempoEstimadoSMaster)
                user_story.tiempoEstimado = float((horas_estimadas_smaster + horas_estimadas_smember) / 2)
                user_story.save()
            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha estimado su User Story con id "
                                                      + user_story.pk + " en el planning poker")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        except Exception as ex:
            messages.error(request, "Error de Token")
            return redirect('home')


class EstimarSprint(View):
    def get(self, request, slug, *args, **kwargs):
        form = EstimacionSprint()
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        horas = 0
        for i in sprint.sprint_backlog.all():
            horas = horas + i.tiempoEstimado

        # proyecto.sprint_actual.duracion_estimada
        context = {
            'horas': horas,
            'form': form,
            'proyecto': proyecto
        }
        return render(request, 'sprint/estimarSprint.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        form = EstimacionSprint(request.POST)

        if form.is_valid():
            horasEstimadas = form.cleaned_data['horas_estimadas']
            sprint.duracion_estimada = horasEstimadas
            sprint.estado = 'conf3'
            sprint.save()
            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha estimado el sprint con id " + sprint.pk)
            messages.success(request, "Se ha asignado la estimación al Sprint")

        else:
            messages.error(request, "Un error a ocurrido")

        return redirect('proyecto_gestion', slug=slug)