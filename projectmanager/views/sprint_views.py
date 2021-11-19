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

from projectmanager.models.user_story_model import RegistroActividadDiairia
from scrum_kanban_pm.settings.development import EMAIL_HOST_USER
from projectmanager.forms import *
from projectmanager.models.user_story_model import RegistroActividadDiairia, logHistorial, UserStorySprint
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
    add_users_to_obj_group, remove_all_perms_from_obj_group, remove_all_users_from_obj_group, \
    calcular_capacidad_desarrollador
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
import numpy, json


class PlanificarSprint(View):
    """
    Vista basada en clase que sirve para la planificacion de sprints.
    """

    def get(self, request, slug, *args, **kwargs):
        """
        Obtiene la instancia del proyecto
        """
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
        """
        Calculo de la capacidad del sprint en horas
        """
        capacidad = 0
        capacidad_dev = {}
        for s_member in proyecto.scrum_member.all():
            capacidad_dev[s_member.username] = 0
        temp_date = fecha_incio
        dia = ''
        while temp_date <= fecha_fin:

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
                    capacidad_dev[work_user.desarrollador.username] += work_user.horas
            temp_date = temp_date + timedelta(days=1)

        if hasattr(proyecto, "siguiente_sprint"):
            messages.error(request, "Ya tienes un sprint planificado")
            return redirect('proyecto_gestion', slug=proyecto.slug)
        elif hasattr(proyecto, "sprint_actual"):
            sprint1 = Sprint.objects.create(fecha_inicio=fecha_incio, fecha_finalizacion=fecha_fin,
                                            fecha_inicio_desarrollo=fecha_incio, fecha_finalizacion_real=fecha_fin,
                                            proyecto=proyecto,
                                            proyecto_sig=proyecto, capacidad_horas=capacidad)
            for s_member in proyecto.scrum_member.all():
                CapacidadSMasteSprint.objects.create(capacidad_horas=capacidad_dev[s_member.username],
                                                     saldo_horas=capacidad_dev[s_member.username],
                                                     sprint=sprint1, scrum_member=s_member)
                sprint1.scrum_member.add(s_member)

            sprint1.save()
        else:
            sprint2 = Sprint.objects.create(fecha_inicio=fecha_incio, fecha_finalizacion=fecha_fin, proyecto=proyecto,
                                            fecha_inicio_desarrollo=fecha_incio, fecha_finalizacion_real=fecha_fin,
                                            proyecto_actual=proyecto, capacidad_horas=capacidad)
            for s_member in proyecto.scrum_member.all():
                CapacidadSMasteSprint.objects.create(capacidad_horas=capacidad_dev[s_member.username],
                                                     sprint=sprint2, scrum_member=s_member,
                                                     saldo_horas=capacidad_dev[s_member.username])
                sprint2.scrum_member.add(s_member)
            sprint2.save()
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
        """
        Obtiene la instancia del UserStory
        """
        ustory = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.cargar_sprint_backlog_proyecto',),
                                      ustory.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=ustory.proyecto.slug)
        sprint = ustory.sprint
        sprint.horas_ocupadas_us -= ustory.tiempoEstimadoSMaster
        if hasattr(ustory, 'desarrolladorAsignado') and ustory.desarrolladorAsignado is not None:
            capacidadsm = CapacidadSMasteSprint.objects.get(sprint=ustory.sprint,
                                                            scrum_member=ustory.desarrolladorAsignado)
            capacidadsm.saldo_horas += ustory.tiempoEstimadoSMaster
            capacidadsm.save()
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
        """
        Obtiene la instancia del UserStory
        """
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
            capacidad = CapacidadSMasteSprint.objects.get(sprint=ustory.sprint, scrum_member=sm_asignado)
            capacidad.saldo_horas -= horasEstimadas
            capacidad.save()
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
        """
        Se obtiene la instancia del proyecto y el sprint
        """
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
                'Realize su estimaciones:\n' + 'Nombre US: ' + us.descripcion + '\n' + 'Proyecto: ' + proyecto.nombre + '\n' + "Link: " + activate_url,
                EMAIL_HOST_USER,
                [us.desarrolladorAsignado.email],
            )
            try:
                email.send(fail_silently=False)
            except Exception as ex:
                sprint.estado = 'conf1'
                sprint.save()
                messages.error(request, "No se pudo enviar vuelva a intentar")
                return redirect('proyecto_gestion', slug=proyecto.slug)
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha iniciado el planning poker en el proyecto " + proyecto.nombre)
        return redirect('proyecto_gestion', slug=proyecto.slug)


class PlanningPokerSMemberView(View):
    """
    Vista basada en clases para la visualizacion de miembros del planning poker
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
                sprint = user_story.sprint
                sprint.horas_ocupadas_us -= user_story.tiempoEstimadoSMaster
                sprint.horas_ocupadas_us += user_story.tiempoEstimado
                capacidad = CapacidadSMasteSprint.objects.get(sprint=sprint,
                                                              scrum_member=user_story.desarrolladorAsignado)
                capacidad.saldo_horas += user_story.tiempoEstimadoSMaster
                capacidad.saldo_horas -= user_story.tiempoEstimado
                capacidad.save()
                sprint.save()

            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha estimado su User Story con id "
                                                      + str(user_story.pk) + " en el planning poker")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        except Exception as ex:
            messages.error(request, "Error de Token")
            print(ex)
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
        sprint.fecha_inicio_desarrollo = timezone.now()
        sprint.duracion_estimada_dias = numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                           sprint.fecha_finalizacion_real.date())
        sprint.estado = 'conf3'

        # Calcular capacidad de sprint
        bandera_suma = True
        fecha_incio = sprint.fecha_inicio_desarrollo
        fecha_fin = sprint.fecha_inicio
        if sprint.fecha_inicio_desarrollo > sprint.fecha_inicio:
            bandera_suma = False
            fecha_fin = sprint.fecha_inicio_desarrollo
            fecha_incio = sprint.fecha_inicio
        capacidad = sprint.capacidad_horas
        capacidad_dev = {}
        for s_member in proyecto.scrum_member.all():
            capacidad_dev_actual = CapacidadSMasteSprint.objects.get(sprint=sprint, scrum_member=s_member)
            capacidad_dev[s_member.username] = capacidad_dev_actual.capacidad_horas
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
                    if bandera_suma:
                        capacidad += work_user.horas
                        capacidad_dev[work_user.desarrollador.username] += work_user.horas
                    else:
                        capacidad -= work_user.horas
                        capacidad_dev[work_user.desarrollador.username] -= work_user.horas
            temp_date = temp_date + timedelta(days=1)

        sprint.save()
        for s_member in sprint.proyecto.scrum_member.all():
            capacidad_dev_x = CapacidadSMasteSprint.objects.get(sprint=sprint, scrum_member=s_member)
            capacidad_dev_x.capacidad_horas += capacidad_dev[s_member.username]
            capacidad_dev_x.saldo_horas += capacidad_dev[s_member.username]
            capacidad_dev_x.save()

        for us in sprint.sprint_backlog.all():
            us.estado = 'To-Do'
            us.save()
            RegistroActividadDiairia.objects.create(us=us, descripcion="Se cambió estado de user story a TO-Do")
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
        """
        Se obtiene la instancia del proyecto y el sprint
        """
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = Sprint.objects.get(pk=sprintPk)
        registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint)
        horas_us_total = 0
        for us in sprint.sprint_backlog.all():
            if not us.tiempoEstimado > 0:
                messages.error(request, "Faltan Estimar User Stories")
                return redirect('proyecto_gestion', slug=slug)
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint.duracion_estimada_dias
        progreso = []
        progreso_act = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
            progreso_act.append(horas_us_total)

        for us in sprint.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0

        for actividad in registros_de_actividad:
            diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                    actividad.fecha.date()))
            for i in range(0, duracionSprint + 1 - diferencia_dia):
                progreso_act[(duracionSprint) - i] -= actividad.hora
        passed_days = duracionSprint

        if sprint.estado == 'fin':
            progreso = sprint.saved_us_progress
            progreso_act = sprint.saved_act_progress
            horas_us_total = sprint.saved_horas_us_total
        data = {
            'dias_estimados': duracionSprint,
            'horas_us_totales': horas_us_total,
            'progreso': progreso,
            'progreso_act': progreso_act,
            'passed_days': passed_days,
            'horas_desarrolladas': 0
        }
        return JsonResponse(data)


class ConfirmarFinalizarSprint(View):
    """
    Vista basada en clase que sirve como una pagina de confirmacion para terminar sprint;
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

        registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint)
        horas_us_total = 0
        for us in sprint.sprint_backlog.all():
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint.duracion_estimada_dias
        progreso = []
        progreso_act = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
            progreso_act.append(horas_us_total)
        for us in sprint.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                print(sprint.fecha_inicio_desarrollo.date())
                print(us.QA.fecha.date())
                print(diferencia_dia)
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0

        for actividad in registros_de_actividad:
            diferencia_dia = int(numpy.busday_count(sprint.fecha_inicio_desarrollo.date(),
                                                    actividad.fecha.date()))
            for i in range(0, duracionSprint + 1 - diferencia_dia):
                progreso_act[(duracionSprint) - i] -= actividad.hora
        passed_days = duracionSprint
        sprint.saved_us_progress = progreso
        sprint.saved_act_progress = progreso_act
        sprint.saved_horas_us_total = horas_us_total
        sprint.fecha_finalizacion_real = timezone.now().date()
        sprint.save()
        if sprint_actual.estado == 'conf3':
            sprint_actual.estado = 'fin'
            for user_story in sprint_actual.sprint_backlog.all():
                if user_story.estado != 'Release':
                    user_story.estado = 'no-terminado'
                    user_story.desarrolladorAsignado = None
                    user_story.save()
                    RegistroActividadDiairia.objects.create(us=user_story, descripcion="Se ")
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

        '''Acá se guardan en la nueva clase UserStorySprint los user storys de cada sprint
        con sus respectivos estados '''
        for us in sprint.sprint_backlog.all():
            usprint = UserStorySprint.objects.create(descripcion=us.descripcion,
                                                     tiempoEstimadoSMaster=us.tiempoEstimadoSMaster,

                                                     desarrolladorAsignado=us.desarrolladorAsignado,
                                                     tiempoEstimado=us.tiempoEstimado, estado=us.estado,
                                                     tiempoEnDesarrollo=us.tiempoEnDesarrollo, proyecto=us.proyecto,
                                                     sprintUs=us.sprint,
                                                     prioridad=us.prioridad, descripcionDone=us.descripcionDone)
            for act in us.RegistroActividad.all():
                RegistroActividadDiairia.objects.create(us2=usprint, descripcion=act.descripcion, fecha=act.fecha,
                                                        hora=act.hora)

        messages.success(request, "Sprint Finalizado")
        return redirect('proyecto_gestion', slug=proyecto.slug)


class VerSprintDetail(View):
    """
    Vista basada en clase para la visualizacion de los
    detalles de un Sprint
    """

    def get(self, request, sprintPk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprintPk)
        proyecto = sprint.proyecto
        if not request.user.has_perms(('projectmanager.ver_proyecto',),
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
        fecha_fin = datetime.datetime.strptime(request.POST.get('fecha_fin'), "%Y-%m-%d")
        sprint.fecha_finalizacion = fecha_fin
        sprint.fecha_finalizacion_real = fecha_fin
        sprint.save()
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha extendido el sprint con id " + str(sprint.pk))
        messages.success(request, "Se ha asignado la estimación al Sprint")

        return redirect('proyecto_gestion', slug=slug)


def get_list_user_current_sprint(request):
    """
    Obtiene todos los usuarios que estan en el sprint actual
    """
    if request.method == "POST":
        body = json.loads(request.body)
        proyecto = Proyecto.objects.get(slug=body['slug'])
        user_list = []
        for us in proyecto.scrum_member.all():
            user_list.append(us.username)
        return JsonResponse({"status": 200, "usuarios": user_list})
    return JsonResponse({"status": 400})


def cambiar_dev_en_US(request):
    """
    Función para cambiar de desarrollador en un user story
    """
    if request.method == "POST":
        body = json.loads(request.body)
        user = User.objects.get(username=body['user'])
        us = UserStory.objects.get(pk=body['id'])
        desarrolladorkue = us.desarrolladorAsignado
        capacidad = CapacidadSMasteSprint.objects.get(sprint=us.sprint, scrum_member=desarrolladorkue)
        capacidad.saldo_horas += us.tiempoEstimado
        capacidad.save()
        capacidadnew = CapacidadSMasteSprint.objects.get(sprint=us.sprint, scrum_member=user)
        capacidadnew.saldo_horas -= us.tiempoEstimado
        capacidadnew.save()
        us.desarrolladorAsignado = user
        remove_all_users_from_obj_group('desarrollador_de_' + str(us.pk))
        add_user_to_obj_group(us.desarrolladorAsignado, 'desarrollador_de_' + str(us.pk))
        us.save()
        return JsonResponse({"status": 200})
    return JsonResponse({"status": 400})
