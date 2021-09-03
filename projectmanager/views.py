from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.db.models import Q

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    TemplateView,
    DetailView
)
from projectmanager.forms import ProyectoForm, ProyectoEditarSMForm, ActualizarUsuarioForm
from projectmanager.forms import ProyectoForm
from .forms import UserForm, RolForm, UserFormDelete
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from .utils import account_activation_token

# Create your views here.
from projectmanager.models import Proyecto, rol

from django.http import JsonResponse
from django.urls import reverse_lazy


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


class ProyectoDetailView(UserAccessMixin, DetailView):
    """
    Presenta la pagina principla para la gestion de un proyecto

    """
    raise_exception = False
    permission_required = ()
    permission_required_obj = ('projectmanager.ver_proyecto',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Proyecto
    template_name = 'proyecto/detail.html'
    context_object_name = 'proyecto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perms(self.permission_required_obj):
            if not request.user.has_perms(self.permission_required_obj, self.object):
                messages.error(request, "No tienes permisos para eso")
                return redirect('/')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


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


class ProyectoSMUpdate(UserAccessMixin, UpdateView):
    """
    Vista basada en clase el sirve para editar un proyecto nuevo por parte del SM

    Atributos:

        Parameters
        ----------
        model
            Modelo a utilizar seria el de Proyecto

        formclass
            El formulario a utilizar es el FormProyecto
    """
    raise_exception = False
    permission_required = ()
    permission_required_obj = ('projectmanager.editar_proyecto',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Proyecto  # Indicar el modelo a utilizar
    form_class = ProyectoEditarSMForm  # Indicar el formulario
    template_name = 'proyecto/detail.html'  # Indicar el template
    success_url = reverse_lazy('proyecto_listar')  # Redireccionar

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perms(self.permission_required_obj):
            if not request.user.has_perms(self.permission_required_obj, self.object):
                messages.error(request, "No tienes permisos para eso")
                return redirect('/')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perms(self.permission_required_obj):
            if not request.user.has_perms(self.permission_required_obj, self.object):
                messages.error(request, "No tienes permisos para eso")
                return redirect('/')
        return super().post(request, *args, **kwargs)


class ProyectoIniciarView(UserAccessMixin, View):
    """
        Vista basada en clase el sirve para iniciar un proyecto nuevo por parte del SM
    """
    raise_exception = False
    permission_required = ()
    permission_required_obj = ('projectmanager.iniciar_proyecto',)
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    def post(self, request, *args, **kwargs):
        project = Proyecto.objects.get(scrum_master=request.user)
        if not request.user.has_perms(self.permission_required_obj):
            if not request.user.has_perms(self.permission_required_obj, project):
                messages.error(request, "No tienes permisos para eso")
                return redirect('/')

        project.estado = 'ACT'
        project.save()
        return redirect(reverse_lazy('proyecto_listar'))


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

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


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
    raise_exception = False
    permission_required = ('projectmanager.quitar_roles')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'
    model = User
    form_class = UserFormDelete
    template_name = 'rol/eliminarRolUser.html'
    success_url = reverse_lazy('list_user')
