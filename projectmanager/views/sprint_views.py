from datetime import timedelta, date, datetime
import pandas as pd
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
from django.utils import timezone
import datetime
import numpy


class PlanificarSprint(View):
    """
    Vista basada en clase que sirve para la planificacion de sprints.
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        context = {
            'proyecto': proyecto
        }
        return render(request, 'sprint/planificar_sprint.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        print(request.POST.get('fecha_inicio'))
        fecha_incio = datetime.datetime.strptime(request.POST.get('fecha_inicio'), "%Y-%m-%d")
        fecha_fin = datetime.datetime.strptime(request.POST.get('fecha_fin'), "%Y-%m-%d")

        # Calcular capacidad de sprint
        capacidad = 0
        temp_date = fecha_incio
        dia = ''
        while temp_date < fecha_fin:

            if temp_date.weekday() == 0:
                dia = 'LUN'
            elif temp_date.weekday() == 1:
                dia = 'MAR'
            elif temp_date.weekday() == 2:
                dia = 'MIE'
            elif temp_date.weekday() == 3:
                dia = 'JUE'
            elif temp_date.weekday() == 4:
                dia = 'VIE'
            else:
                dia = ''

            for work_user in proyecto.tiempos_de_usuarios.all():
                if work_user.dia == dia:
                    capacidad += work_user.horas
            temp_date = temp_date + timedelta(days=1)

        if hasattr(proyecto, "siguiente_sprint"):
            messages.error(request, "Ya tienes un sprint planificado")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        elif hasattr(proyecto, "sprint_actual"):
            Sprint.objects.create(fecha_inicio=fecha_incio, fecha_finalizacion=fecha_fin, proyecto=proyecto,
                                  proyecto_sig=proyecto, capacidad_horas=capacidad)
        else:
            Sprint.objects.create(fecha_inicio=fecha_incio, fecha_finalizacion=fecha_fin, proyecto=proyecto,
                                  proyecto_actual=proyecto, capacidad_horas=capacidad)
        return redirect('proyecto_gestion', slug=slug)


class CargarSprintBacklog(View):
    """
    Vista basada en clase que sirve para cargar el sprint backlog
    """

    def post(self, request, usPk, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        proyecto = sprint.proyecto
        print(proyecto)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        sprint_selected = request.POST.get("sprintx")
        if sprint_selected == "2":
            sprint = sprint.proyecto_actual.siguiente_sprint
        if sprint.estado != 'conf1':
            messages.error(request, "Ya no puedes agregar user stories al sprint backlog")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        ustory = UserStory.objects.get(pk=usPk)
        ustory.sprint = sprint
        ustory.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha agregado el user story con id " + str(ustory.pk)
                                                  + " al sprint backlog del proyecto " + proyecto.nombre)
        messages.success(request, 'User Story agregado al SprintBacklog')
        return redirect('proyecto_gestion', slug=proyecto.slug)


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
        sprint = ustory.sprint
        sprint.horas_ocupadas_us -= ustory.tiempoEstimadoSMaster
        ustory.sprint = None
        ustory.desarrolladorAsignado = None
        ustory.tiempoEstimado = 0
        ustory.save()
        sprint.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha removido el user story con id " + str(ustory.pk)
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
            sprint = ustory.sprint
            sprint.horas_ocupadas_us += horasEstimadas
            sprint.save()
            ustory.save()
            add_obj_perm_to_group('desarrollador_de_' + str(ustory.pk), 'desarrollar_user_story', ustory)
            add_user_to_obj_group(ustory.desarrolladorAsignado, 'desarrollador_de_' + str(ustory.pk))
        else:
            messages.error(request, "Un error a ocurrido")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha asginado y estimado el user story con id " + str(ustory.pk)
                                                  + " del sprint backlog del proyecto " + ustory.proyecto.nombre)
        messages.success(request, "Se ha asignado y estimado el User Story")
        return redirect('proyecto_gestion', slug=ustory.proyecto.slug)


class PlanningPokerView(View):
    """
    Vista basada en clase para la gestion de planning poker
    """

    def get(self, request, slug, sprintPk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = Sprint.objects.get(pk=sprintPk)
        if not request.user.has_perms(('projectmanager.iniciar_ppoker_proyecto',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        if not sprint.sprint_backlog.exists():
            messages.error(request, 'No tienes user stories!')
            return redirect('proyecto_gestion', slug=proyecto.slug)
        if sprint.estado != 'conf1':
            messages.error(request, 'No se puede realizar planning poker')
            return redirect('proyecto_gestion', slug=proyecto.slug)
        for us in sprint.sprint_backlog.all():
            if not us.desarrolladorAsignado != None:
                messages.error(request, "Debes asignar todos los User Stories")
                return redirect('proyecto_gestion', slug=slug)
        sprint.estado = 'conf2'
        sprint.save()
        for us in sprint.sprint_backlog.all():
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
            ustory.tiempoEstimado = 0
            ustory.save()
            if ustory.tiempoEstimado != 0 and ustory.tiempoEstimado is not None:
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
            print(ex)
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
            sprint = user_story.sprint
            sprint.horas_ocupadas_us -= user_story.tiempoEstimadoSMaster
            sprint.horas_ocupadas_us += user_story.tiempoEstimado
            sprint.save()
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha estimado su User Story con id "
                                                      + str(user_story.pk) + " en el planning poker")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        except Exception as ex:
            messages.error(request, "Error de Token")
            return redirect('home')


class EstimarSprint(View):
    """
    Vista basada en clase utilizada para la estimacion de sprint
    """

    def get(self, request, slug, *args, **kwargs):
        form = EstimacionSprint()
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        horas_us_total = 0
        horas_desarrolladores = 0
        horas_por_dia = {'lun': 0,
                         'mar': 0,
                         'mie': 0,
                         'jue': 0,
                         'vie': 0}
        for us in sprint.sprint_backlog.all():
            if not us.tiempoEstimado > 0:
                messages.error(request, "Faltan Estimar User Stories")
                return redirect('proyecto_gestion', slug=slug)
            horas_us_total = horas_us_total + us.tiempoEstimado
        for tiempo in proyecto.tiempos_de_usuarios.all():
            horas_desarrolladores += tiempo.horas
            if tiempo.dia == 'LUN':
                horas_por_dia['lun'] += tiempo.horas
            if tiempo.dia == 'MAR':
                horas_por_dia['mar'] += tiempo.horas
            if tiempo.dia == 'MIE':
                horas_por_dia['mie'] += tiempo.horas
            if tiempo.dia == 'JUE':
                horas_por_dia['jue'] += tiempo.horas
            if tiempo.dia == 'VIE':
                horas_por_dia['vie'] += tiempo.horas
        today = datetime.datetime.today().weekday()
        print(today)
        if today == 5 or today == 6:
            today = 0
        # proyecto.sprint_actual.duracion_estimada
        context = {
            'horas': horas_us_total,
            'horas_desarrolladores': horas_desarrolladores,
            'horas_por_dia': horas_por_dia,
            'hoy': today,
            'form': form,
            'proyecto': proyecto
        }
        return render(request, 'sprint/estimarSprint.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        form = EstimacionSprint(request.POST)

        sprint.duracion_estimada_dias = numpy.busday_count(sprint.fecha_inicio.date(),
                                                           sprint.fecha_finalizacion.date())
        sprint.fecha_inicio_desarrollo = timezone.now().date()
        sprint.estado = 'conf3'

        sprint.save()
        for us in sprint.sprint_backlog.all():
            us.estado = 'To-Do'
            us.save()
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha estimado el sprint con id " + str(sprint.pk))
        messages.success(request, "Se ha asignado la estimación al Sprint")

        return redirect('proyecto_gestion', slug=slug)


class VerBurndownChartView(View):
    """
    Vista basada en clase para la visusalizacion del burndownchart
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        context = {
            'proyecto': proyecto
        }
        return render(request, 'sprint/burndown_chart.html', context)


class getDataForBurndownChart(View):
    """
    Vista basada en clase para la obtención de los datos para el burndownchart
    """

    def get(self, request, slug, sprintPk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = Sprint.objects.get(pk=sprintPk)
        horas_us_total = 0
        for us in sprint.sprint_backlog.all():
            if not us.tiempoEstimado > 0:
                messages.error(request, "Faltan Estimar User Stories")
                return redirect('proyecto_gestion', slug=slug)
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint.duracion_estimada_dias
        progreso = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
        for us in sprint.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0
        passed_days = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                             datetime.datetime.now(timezone.utc).date()))
        if sprint.estado == 'fin':
            progreso = sprint.saved_us_progress
            horas_us_total = sprint.saved_horas_us_total
        data = {
            'dias_estimados': duracionSprint,
            'horas_us_totales': horas_us_total,
            'progreso': progreso,
            'passed_days': passed_days,
            'horas_desarrolladas': 0
        }
        return JsonResponse(data)


class ConfirmarFinalizarSprint(View):
    """
    Vista basada en clase que sirve una pagina de confirmacion para terminar sprint;
    """

    def get(self, request, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        proyecto = sprint.proyecto_actual
        if not request.user.has_perms(('projectmanager.finalizar_sprint',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        context = {
            'sprint': Sprint.objects.get(pk=sprintPk)
        }
        return render(request, 'sprint/sprint_confirmar_finalizar.html', context)


class FinalizarSprint(View):
    """
    Vista Basada en clase que finaliza un sprint;
    """

    def get(self, request, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        proyecto = sprint.proyecto_actual
        sprint_actual = proyecto.sprint_actual
        if hasattr(proyecto, "siguiente_sprint"):
            sprint_sig = proyecto.siguiente_sprint
        if not request.user.has_perms(('projectmanager.finalizar_sprint',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')

        horas_us_total = 0
        for us in sprint.sprint_backlog.all():
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint.duracion_estimada_dias
        progreso = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
        for us in sprint.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0
        sprint.saved_us_progress = progreso
        sprint.saved_horas_us_total = horas_us_total
        sprint.save()
        if sprint_actual.estado == 'conf3':
            sprint_actual.estado = 'fin'
            for user_story in sprint_actual.sprint_backlog.all():
                if user_story.estado != 'Release':
                    user_story.estado = 'no-terminado'
                    user_story.desarrolladorAsignado = None
                    user_story.save()
            sprint_actual.proyecto_actual = None
            sprint_actual.fecha_finalizacion_real = timezone.now().date()
            sprint_actual.save()
            if hasattr(proyecto, "siguiente_sprint"):
                if proyecto.siguiente_sprint is not None:
                    sprint_sig.proyecto_actual = proyecto
                    sprint_sig.proyecto_sig = None
                    sprint_sig.save()
            proyecto.save()
        else:
            messages.error(request, "Sprint no se puede finalizar")
            return redirect('proyecto_gestion', slug=proyecto.slug)

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Se a finalizado sprint en proyecto " + proyecto.nombre)

        messages.success(request, "Sprint Finalizado")
        return redirect('proyecto_gestion', slug=proyecto.slug)


class VerSprintDetail(View):
    """
    Vista basada en clase para la visualizacion de los
    detalles de un Sprint
    """

    def get(self, request, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        proyecto = sprint.proyecto_actual
        if not request.user.has_perms(('projectmanager.finalizar_sprint',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        context = {
            'sprint': Sprint.objects.get(pk=sprintPk)
        }
        return render(request, 'sprint/sprint_detail.html', context)


class ExtenderSprint(View):
    """
    Viusta basada en clase para la exxtension de tiempo
    de un sprint en caso de que ya llegue a su limite
    """

    def get(self, request, slug, *args, **kwargs):
        form = EstimacionSprint()
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        horas_us_total = 0
        horas_desarrolladas = 0
        horas_desarrolladores = 0
        horas_por_dia = {'lun': 0,
                         'mar': 0,
                         'mie': 0,
                         'jue': 0,
                         'vie': 0}
        for us in sprint.sprint_backlog.all():
            if not us.tiempoEstimado > 0:
                messages.error(request, "Faltan Estimar User Stories")
                return redirect('proyecto_gestion', slug=slug)
            horas_us_total = horas_us_total + us.tiempoEstimado
            if us.estado == 'Release':
                horas_desarrolladas += us.tiempoEstimado
        for tiempo in proyecto.tiempos_de_usuarios.all():
            horas_desarrolladores += tiempo.horas
            if tiempo.dia == 'LUN':
                horas_por_dia['lun'] += tiempo.horas
            if tiempo.dia == 'MAR':
                horas_por_dia['mar'] += tiempo.horas
            if tiempo.dia == 'MIE':
                horas_por_dia['mie'] += tiempo.horas
            if tiempo.dia == 'JUE':
                horas_por_dia['jue'] += tiempo.horas
            if tiempo.dia == 'VIE':
                horas_por_dia['vie'] += tiempo.horas
        today = datetime.datetime.today().weekday()
        print(today)
        if today == 5 or today == 6:
            today = 0
        # proyecto.sprint_actual.duracion_estimada
        context = {
            'horas': horas_us_total,
            'horas_desarrolladores': horas_desarrolladores,
            'horas_por_dia': horas_por_dia,
            'horas_por_desarrollar': horas_us_total - horas_desarrolladas,
            'hoy': today,
            'form': form,
            'proyecto': proyecto
        }
        return render(request, 'sprint/extenderSprint.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        form = EstimacionSprint(request.POST)

        if form.is_valid():
            diasEstimados = form.cleaned_data['dias_estimados']
            sprint.duracion_estimada_dias += diasEstimados
            sprint.fecha_finalizacion = timezone.now().date() + timedelta(hours=sprint.duracion_estimada_dias * 24 + 16)
            sprint.save()
            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha extendido el sprint con id " + str(sprint.pk))
            messages.success(request, "Se ha asignado la estimación al Sprint")

        else:
            messages.error(request, "Un error a ocurrido")

        return redirect('proyecto_gestion', slug=slug)
