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
from django.utils import timezone


class ProyectoCreate(UserAccessMixin, CreateView):
    """
        Vista basada en clase para la creacion de un proyecto nuevo
        Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Proyecto

        formclass
            El formulario a utilizar es el FormProyecto
    """
    raise_exception = False
    permission_required = ('projectmanager.crear_proyecto',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Proyecto
    form_class = ProyectoForm
    template_name = "proyecto/proyecto_form.html"
    success_url = reverse_lazy('proyecto_listar')

    def post(self, request, *args, **kwargs):
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha creado un proyecto")
        return super().post(self, request, *args, **kwargs)


class ProyectoView(UserAccessMixin, ListView):
    """
    Vista basada en clase que lista todos lo proyectos y los muesrra

        Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Proyecto
    """

    raise_exception = False
    permission_required = ('projectmanager.ver_proyectos',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    #:EL modelo base a utilizar es el de Proyecto
    model = Proyecto
    template_name = 'proyecto/proyecto_list.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Administrador').exists():
            return Proyecto.objects.all()
        return Proyecto.objects.filter(Q(scrum_master=self.request.user) | Q(scrum_member=self.request.user)).distinct()


class ProyectoUpdate(UserAccessMixin, UpdateView):
    """
    Vista basada en clase el sirve para la modificacion de un proyecto en especifico

    Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Proyecto

        formclass
            El formulario a utilizar es el FormProyecto
    """
    raise_exception = False
    permission_required = ('projectmanager.editar_proyecto',)
    permission_required_obj = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Proyecto  # Indicar el modelo a utilizar
    form_class = ProyectoForm  # Indicar el formulario
    template_name = 'proyecto/proyecto_form.html'  # Indicar el template
    success_url = reverse_lazy('proyecto_listar')  # Redireccionar

    extra_context = {}

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.estado != 'PEN':
            return super().get(request, *args, **kwargs)
        messages.error(request, "No se puede editar este proyecto")
        return redirect('proyecto_gestion', slug=self.object.slug)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.estado != 'PEN':
            # Log activity
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha modificado el proyecto " + self.object.nombre)
            return super().get(request, *args, **kwargs)
        messages.error(request, "No se puede editar este proyecto")
        return redirect('proyecto_gestion', slug=self.object.slug)

    # def get_context_data(self, **kwargs):
    #     context = super(ExtraContext, self).get_context_data(**kwargs)
    #     context.update(self.extra_context)
    #     return context


class GestionProyectoView(UserAccessMixin, View):
    """
        Vista Que Administra la pantalla de gestion de proyecto
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.ver_proyecto',), proyecto) and not request.user.groups.filter(
                name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        tiempos_totales = {}
        for scrum_member in proyecto.scrum_member.all():
            for work in scrum_member.tiempos_de_trabajo.all():
                if work.proyecto == proyecto:
                    tiempos_totales[scrum_member.username] = work.totalEnProyecto
        finalizar = True
        if proyecto.estado != 'ACT':
            finalizar = False
        for us in proyecto.product_backlog.all():
            if us.estado != 'Release':
                finalizar = False
        if hasattr(proyecto, 'sprint_actual'):
            if proyecto.sprint_actual.estado != 'conf1':
                finalizar = False
        context = {
            'proyecto': proyecto,
            'finalizar': finalizar
        }
        return render(request, 'proyecto/gestion_proyecto.html', context)


class AgregarSMember(UserAccessMixin, View):
    """
    Vista basada en clase el sirve para editar un proyecto nuevo por parte del SM

    Atributos:

        Parameters
        ----------

        formclass
            El formulario a utilizar es el FormProyecto
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        users_work = []
        for user in User.objects.all():
            if user.username != 'AnonymousUser' and user.username != 'admin':
                x = {'usuario': user.username,
                     'LUN': 0,
                     'MAR': 0,
                     'MIE': 0,
                     'JUE': 0,
                     'VIE': 0}
                users_work.append(x)
                for work in user.tiempos_de_trabajo.all():
                    x[work.dia] += work.horas
        form = AgregarScrumMemberForm(slug=slug)
        context = {
            'proyecto': proyecto,
            'users_work': users_work,
            'form': form
        }
        return render(request, 'proyecto/agregar_scrum_member.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        form = AgregarScrumMemberForm(request.POST, slug=slug)
        confirmation = False
        if form.is_valid():
            scrum_member = form.cleaned_data['scrum_member']
            lunes = form.cleaned_data['lunes']
            martes = form.cleaned_data['martes']
            miercoles = form.cleaned_data['miercoles']
            jueves = form.cleaned_data['jueves']
            viernes = form.cleaned_data['viernes']
            if lunes < 0 or martes < 0 or miercoles < 0 or jueves < 0 or viernes < 0:
                messages.error(request, 'No puedes ingresar numeros negativos')
                return redirect('proyecto_agregar_sm', slug=proyecto.slug)
            if lunes == 0 and martes == 0 and miercoles == 0 and jueves == 0 and viernes == 0:
                messages.error(request, 'Agrega horas de trabajo')
                return redirect('proyecto_agregar_sm', slug=proyecto.slug)
            worktimes = scrum_member.tiempos_de_trabajo.all()
            horas_ocupadas_lunes = 0
            horas_ocupadas_martes = 0
            horas_ocupadas_miercoles = 0
            horas_ocupadas_jueves = 0
            horas_ocupadas_viernes = 0
            for worktime in worktimes:
                if worktime.dia == 'LUN':
                    horas_ocupadas_lunes += worktime.horas
                elif worktime.dia == 'MAR':
                    horas_ocupadas_martes += worktime.horas
                elif worktime.dia == 'MIE':
                    horas_ocupadas_miercoles += worktime.horas
                elif worktime.dia == 'JUE':
                    horas_ocupadas_jueves += worktime.horas
                elif worktime.dia == 'VIE':
                    horas_ocupadas_viernes += worktime.horas
            if horas_ocupadas_lunes + lunes > 8:
                messages.error(request,
                               'Este usuario tiene ' + str(horas_ocupadas_lunes) +
                               ' hs ocupadas los lunes, puede tener hasta ' + str(8.0 - horas_ocupadas_lunes) +
                               ' hs agregadas.')
                return redirect('proyecto_agregar_sm', slug=slug)
            if horas_ocupadas_martes + martes > 8:
                messages.error(request,
                               'Este usuario tiene ' + str(horas_ocupadas_martes) +
                               ' hs ocupadas los martes, puede tener hasta ' + str(8.0 - horas_ocupadas_martes) +
                               ' hs agregadas.')
                return redirect('proyecto_agregar_sm', slug=slug)
            if horas_ocupadas_miercoles + miercoles > 8:
                messages.error(request,
                               'Este usuario tiene ' + str(horas_ocupadas_miercoles) +
                               ' hs ocupadas los miercoles, puede tener hasta ' + str(8.0 - horas_ocupadas_miercoles) +
                               ' hs agregadas.')
                return redirect('proyecto_agregar_sm', slug=slug)
            if horas_ocupadas_jueves + jueves > 8:
                messages.error(request,
                               'Este usuario tiene ' + str(horas_ocupadas_jueves) +
                               ' hs ocupadas los jueves, puede tener hasta ' + str(8.0 - horas_ocupadas_jueves) +
                               ' hs agregadas.')
                return redirect('proyecto_agregar_sm', slug=slug)
            if horas_ocupadas_viernes + viernes > 8:
                messages.error(request,
                               'Este usuario tiene ' + str(horas_ocupadas_viernes) +
                               ' hs ocupadas los viernes, puede tener hasta ' + str(8.0 - horas_ocupadas_viernes) +
                               ' hs agregadas.')
                return redirect('proyecto_agregar_sm', slug=slug)
            horas_totales = lunes + martes + miercoles + jueves + viernes

            UserWorkTime.objects.create(proyecto=proyecto, desarrollador=scrum_member, dia='LUN', horas=lunes,
                                        totalEnProyecto=horas_totales)
            UserWorkTime.objects.create(proyecto=proyecto, desarrollador=scrum_member, dia='MAR', horas=martes,
                                        totalEnProyecto=horas_totales)
            UserWorkTime.objects.create(proyecto=proyecto, desarrollador=scrum_member, dia='MIE', horas=miercoles,
                                        totalEnProyecto=horas_totales)
            UserWorkTime.objects.create(proyecto=proyecto, desarrollador=scrum_member, dia='JUE', horas=jueves,
                                        totalEnProyecto=horas_totales)
            UserWorkTime.objects.create(proyecto=proyecto, desarrollador=scrum_member, dia='VIE', horas=viernes,
                                        totalEnProyecto=horas_totales)
            proyecto.scrum_member.add(scrum_member)
            proyecto.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha agregado Scrum Members al proyecto " + proyecto.nombre)

        messages.success(request, 'Scrum Member agregado')
        return redirect('proyecto_gestion', slug=slug)


class QuitarSMember(View):
    """
        Vista basada en clase para quitar un Scrum Member
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        form = QuitarScrumMemberForm(slug=slug)
        context = {
            'proyecto': proyecto,
            'form': form
        }
        return render(request, 'proyecto/agregar_scrum_member.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        form = QuitarScrumMemberForm(request.POST, slug=slug)
        if form.is_valid():
            scrum_member = form.cleaned_data['scrum_member']
            for user_story in scrum_member.desarrollador_asignado.all():
                if user_story.proyecto == proyecto:
                    messages.error(request, "Este usuario tiene user stories asignados")
                    return redirect('proyecto_quitar_sm', slug=slug)
            for work in scrum_member.tiempos_de_trabajo.all():
                if work.proyecto == proyecto:
                    work.delete()
            proyecto.scrum_member.remove(scrum_member)
            scrum_member.save()
            proyecto.save()

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha quitado scrum members del proyecto " + proyecto.name)
        messages.success(request, 'Scrum Member removido')
        return redirect('proyecto_gestion', slug=slug)


# TO-DO: Quitar editar cuando se inicie el proyecto y habilitar sprint
class ProyectoIniciarView(UserAccessMixin, View):
    """
        Vista basada en clase el sirve para iniciar un proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.iniciar_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')

        if proyecto.estado == 'PEN':
            proyecto.estado = 'ACT'
            proyecto.save()
        else:
            messages.error(request, "Proyecto no se puede iniciar")
            return redirect('proyecto_gestion', slug=slug)

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha iniciado el proyecto " + proyecto.nombre)

        messages.success(request, "Proyecto Iniciado")
        return redirect('proyecto_gestion', slug=proyecto.slug)


class ProyectoCancelarView(UserAccessMixin, View):
    """
    Vista Basada en clase que sirve para cancelar un proyecto con estado pendiente
    """
    raise_exception = False
    permission_required = ('projectmanager.cancelar_proyecto',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if proyecto.estado == 'PEN':
            proyecto.estado = 'CAN'
            for scrum_member in proyecto.scrum_member.all():
                for work in scrum_member.tiempos_de_trabajo.all():
                    if work.proyecto == proyecto:
                        work.delete()
            proyecto.save()
        else:
            messages.error(request, "Proyecto no se puede cancelar")
            return redirect('proyecto_gestion', slug=slug)

        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha cancelado el proyecto " + proyecto.nombre)

        messages.success(request, "Proyecto Cancelado")
        return redirect('proyecto_listar')


class FinalizarProyecto(View):
    """
    Vista basada en clases utilizada para la
    finalizacion de un prouectp
    """

    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        for us in proyecto.product_backlog.all():
            if us.estado != 'Release':
                messages.error(request, "Proyecto no se puede finalizar")
                return redirect('proyecto_gestion', slug=slug)
        if proyecto.sprint_actual.estado != 'conf1':
            messages.error(request, "Proyecto no se puede finalizar")
            return redirect('proyecto_gestion', slug=slug)
        count = 0
        sprint_cantidad = proyecto.product_backlog.count()
        for us in proyecto.product_backlog.all():
            count += us.tiempoEstimado
        context = {
            'proyecto': proyecto,
            'horas': count,
            'sprints_realizados': sprint_cantidad
        }
        return render(request, 'proyecto/finalizar_proyecto.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        proyecto.estado = 'FIN'
        proyecto.sprint_actual.delete()
        proyecto.fecha_fin = timezone.now().date()
        for uw in proyecto.tiempos_de_usuarios.all():
            uw.delete()
        proyecto.save()

        return redirect('proyecto_gestion', slug=slug)
