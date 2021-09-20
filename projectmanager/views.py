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
from .forms import UserForm, RolForm, UserFormDelete
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token, add_user_to_obj_group, add_perm_to_group, add_obj_perm_to_group, \
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


# class ProyectoDetailView(UserAccessMixin, DetailView):
#     """
#     Presenta la pagina principla para la gestion de un proyecto
#
#     """
#     raise_exception = False
#     permission_required = ()
#     permission_required_obj = ('projectmanager.ver_proyecto',)
#     permission_denied_message = "You don't have permissions"
#     redirect_field_name = 'next'
#
#     model = Proyecto
#     template_name = 'proyecto/detail.html'
#     context_object_name = 'proyecto'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         return context
#
#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if not request.user.has_perms(self.permission_required_obj):
#             if not request.user.has_perms(self.permission_required_obj, self.object):
#                 messages.error(request, "No tienes permisos para eso")
#                 return redirect('/')
#         context = self.get_context_data(object=self.object)
#         return self.render_to_response(context)


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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.estado != 'PEN':
            return super().get(request, *args, **kwargs)
        messages.error(request, "No se puede editar este proyecto")
        return redirect('proyecto_gestion', slug=self.object.slug)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.estado != 'PEN':
            return super().get(request, *args, **kwargs)
        messages.error(request, "No se puede editar este proyecto")
        return redirect('proyecto_gestion', slug=self.object.slug)


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
        context = {
            'proyecto': proyecto
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
        form = AgregarScrumMemberForm(slug=slug)
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
        form = AgregarScrumMemberForm(request.POST, slug=slug)
        confirmation = False
        if form.is_valid():
            scrum_member = form.cleaned_data['scrum_member']
            lunes = form.cleaned_data['lunes']
            martes = form.cleaned_data['martes']
            miercoles = form.cleaned_data['miercoles']
            jueves = form.cleaned_data['jueves']
            viernes = form.cleaned_data['viernes']
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

        messages.success(request, 'Scrum Member agregado')
        return redirect('proyecto_gestion', slug=slug)


class QuitarSMember(View):
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
            sprint = Sprint.objects.create(proyecto=proyecto, proyecto_actual=proyecto)
            proyecto.save()
        else:
            messages.error(request, "Proyecto no se puede iniciar")
            return redirect('proyecto_gestion', slug=slug)
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
            proyecto.save()
        else:
            messages.error(request, "Proyecto no se puede cancelar")
            return redirect('proyecto_gestion', slug=slug)
        messages.success(request, "Proyecto Cancelado")
        return redirect('proyecto_listar')


@login_required
def perfilUsuario(request):
    if request.method == "POST":
        form = ActualizarUsuarioForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Tu información ha sido actualizada!")
            return redirect("perfil")
    else:
        form = ActualizarUsuarioForm(instance=request.user)
    return render(request, "perfil/usuario.html", {'form': form})


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


# VISTAS DE  USERS STORYS

class UserStoryCreate(View):
    '''

    Vista para crear y listar User Storys
    US:obtiene todos los USER STORYS en el metodo get y lista los USER STORYS
    En el metodo post se obtiene el proyecto en el que se está trabajando y se crea una
    instancia de USER STORY y se le asigna los datos correspondientes del form y tambien el proyecto
    al cual pertenece

    '''

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
                messages.success(request, "User Story Creado Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class UserStoryUpdate(View):
    '''

        Vista para actualizar los datos de descripcion y prioridad de un User Story
        US:obtiene el user story con metodo get y su pk
        En el metodo post se obtiene el objeto del User Story actual y se actualiza
        con los nuevos datos de entrada

        '''

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
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
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
        form = ProyectoUs(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripción_de_user_story']
            prioridad = form.cleaned_data['prioridad_1_al_10']
            if prioridad > 0 and prioridad < 11:
                nuevoHistorial = HistorialUs(us=US2,descripcion=US2.descripcion)
                nuevoHistorial.save()
                US2.descripcion = descripcion
                US2.prioridad=prioridad

                US2.save()
                messages.success(request, "User Story se actualizó Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")

        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class EliminarUs(View):
    '''

        Clase para eliminar un user story
        Se obtiene el objeto por su pk y se hace un delete

    '''

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US = UserStory.objects.get(pk=pk)
        US.delete()
        messages.success(request, "User Story Eliminado")
        return redirect('create_us', slug=slug)


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
        related_group = rol.related_group
        related_group.delete()
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
            messages.success(request, "Roles Importados Correctamente!")
        return redirect('proyecto_rol', slug=slug)


class CrearSprint(View):
    def get(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        sprint = Sprint.objects.all()
        form = SprintFormCreate(slug=slug)
        context = {
            'form': form,
            'proyecto': proyecto,
            'sprint': sprint
        }
        return render(request, 'sprint/crearSprint.html', context)

    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        form = SprintFormCreate(request.POST, slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            US = form.cleaned_data['UserStorys']
            # duracion_estimada = form.cleaned_data['duracion_estimanda']
            validar = Sprint.objects.filter(nombre=nombre).exists()
            if (validar):
                messages.error(request, "Ya existe Sprint con ese nombre")
            else:

                sprint = Sprint.objects.create(nombre=nombre, proyecto=proyecto)
                sprint.save()
                for us in US:
                    userStory = UserStory.objects.get(nombre=us)
                    userStory.sprint = sprint
                    userStory.save()
                messages.success(request, "Sprint Creado Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('crear_sprint', slug=slug)


class ActualizarSprint(View):

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        sprint = Sprint.objects.get(pk=pk)
        form = SprintFormCreate(initial={'nombre': sprint.nombre,
                                         'UserStorys': sprint.Sprint.all(),
                                         'duracion_estimanda': sprint.duracion_estimada}, slug=slug)
        context = {
            'form': form,
            'proyecto': proyecto,
            'sprint': sprint
        }
        return render(request, 'sprint/actualizarSprint.html', context)

    def post(self, request, slug, pk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=pk)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      sprint.proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)

        form = SprintFormCreate(request.POST, slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            US = form.cleaned_data['UserStorys']
            duracion_estimada = form.cleaned_data['duracion_estimanda']
            sprint.nombre = nombre
            sprint.duracion_estimada = duracion_estimada
            sprint.save()
            for us in Sprint.objects.get(pk=pk).Sprint.all():
                userStory = UserStory.objects.get(nombre=us)
                userStory.sprint = None
                userStory.save()
            for us in US:
                userStory = UserStory.objects.get(nombre=us)
                userStory.sprint = sprint
                userStory.save()

            messages.success(request, "User Story se actualizó Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('crear_sprint', slug=slug)


class listaUsSprintBacklog(View):
    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        sprint = Sprint.objects.get(pk=pk).Sprint.all()
        # form=SprintFormCreate(slug=slug)
        context = {
            'proyecto': proyecto,
            'US': sprint
        }
        return render(request, 'sprint_backlog/userStorySprint.html', context)


class UserStoryUpdateSprint(View):
    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_sprint_proyecto',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_rol', slug=slug)
        US = UserStory.objects.all()
        US2 = UserStory.objects.get(pk=pk)
        form = AsignarDesarrolladorUs(slug=slug)
        context = {
            'form': form,
            'proyecto': proyecto,
            'US2': US2
        }
        return render(request, 'sprint_backlog/updateUsSprint.html', context)

    def post(self, request, slug, pk, *args, **kwargs):
        US2 = UserStory.objects.get(pk=pk)
        form = AsignarDesarrolladorUs(request.POST, slug=slug)
        if form.is_valid():
            desarrollador = form.cleaned_data['desarrolladorAsignado']
            US2.desarrolladorAsignado = desarrollador
            US2.save()
            messages.success(request, "User Story se actualizó Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('sprint_backlog', slug=slug, pk=US2.sprint.pk)


class CargarSprintBacklog(View):
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
        messages.success(request, 'User Story agregado al SprintBacklog')
        return redirect('proyecto_gestion', slug=sprint.proyecto_actual.slug)


class QuitarUSFromSprintBacklog(View):
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
        messages.success(request, 'User Story removido del SprintBacklog')
        return redirect('proyecto_gestion', slug=ustory.proyecto.slug)


class listarHistorial(View):
    def get(self,request,slug,pk):
        proyecto = Proyecto.objects.get(slug=slug)
        ustory=UserStory.objects.get(pk=pk).UsHistorial.all()
        print(ustory)
        context={
            'history':ustory,
            'proyecto':proyecto
        }
        return render(request,'UserStory/historial.html',context)


class AsignarYEstimarUserStoryView(View):
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
        messages.success(request, "Se ha asignado y estimado el User Story")
        return redirect('proyecto_gestion', slug=ustory.proyecto.slug)


class PlanningPokerView(View):
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
        return redirect('proyecto_gestion', slug=proyecto.slug)


class PlanningPokerSMemberView(View):
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
            'form': form
        }
        return render(request, 'sprint/estimarSprint.html', context)
    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = proyecto.sprint_actual
        form=EstimacionSprint(request.POST)

        if form.is_valid():
            horasEstimadas = form.cleaned_data['horas_estimadas']
            sprint.duracion_estimada=horasEstimadas
            sprint.estado='conf3'
            sprint.save()
            messages.success(request, "Se ha asignado la estimación al Sprint")
        else:
            messages.error(request, "Un error a ocurrido")

        return redirect('proyecto_gestion', slug=slug)
