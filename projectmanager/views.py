from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib import messages


from django.views.generic import (
    ListView,
    CreateView,
    UpdateView
)
from projectmanager.forms import ProyectoForm
from .forms import UserForm, RolForm
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


def homepage(request):
    """
    Devuelve la pagina principal de la aplicacion

    Parameters
    ----------
    request
        Objeto que contiene info acerca de la solicitud del cliente

    """
    return render(request, "dashboard/home.html")


def proyecto_detail(request, proyecto_slug):
    """
        Presenta la pagina principla para la gestion de un proyecto
    """



    proyecto = get_object_or_404(Proyecto, slug=proyecto_slug)
    return render(request, 'proyecto/detail.html', {'proyecto': proyecto})


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
    permission_required = ('projectmanager.crear_proyecto')
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
    permission_required = ('projectmanager.ver_proyectos')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'


    #:EL modelo base a utilizar es el de Proyecto
    model = Proyecto
    template_name = 'proyecto/proyecto_list.html'

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
    permission_required = ('projectmanager.editar_proyecto')
    permission_denied_message = "You don't have permissions"
    redirect_field_name = 'next'

    model = Proyecto #Indicar el modelo a utilizar
    form_class = ProyectoForm #Indicar el formulario
    template_name = 'proyecto/proyecto_form.html' #Indicar el template
    success_url = reverse_lazy('proyecto_listar') #Redireccionar

class RolListView(ListView):
    model = rol
    template_name = 'rol/list.html'


class RolCreateView(CreateView):
    model = rol
    form_class = RolForm
    template_name = 'rol/create.html'
    success_url = reverse_lazy('list_rol')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class RolUpdateView(UpdateView):
    model = rol
    form_class = RolForm
    template_name = 'rol/update.html'
    success_url = reverse_lazy('list_rol')


class RolDeleteView(DeleteView):
    model = rol
    template_name = 'rol/delete.html'
    success_url = reverse_lazy('list_rol')




class ListUser(ListView):
    model = User
    #form_class = UserForm
    template_name = 'rol/list_user.html'

class AsignarRol(UpdateView):
    model = User
    form_class = UserForm
    template_name = 'rol/asignarRol.html'
    success_url = reverse_lazy('list_user')

