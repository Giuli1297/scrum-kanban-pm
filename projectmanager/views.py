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

from projectmanager.forms import *
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
# Create your views here.
from projectmanager.models import *

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
        context = {
            'proyecto': proyecto
        }
        return render(request, 'proyecto/gestion_proyecto.html', context)


class AgregarSMember(UserAccessMixin, UpdateView):
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
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      self.object) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perms(('projectmanager.gestionar_scrum_members',),
                                      self.object) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('/')
        return super().post(request, *args, **kwargs)


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
            messages.error(request, "Proyecto no se puede cancelar")
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
    US:obtiene todos los USER STORYS en el metodo get y lisata los USER STORYS
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
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            validar=UserStory.objects.filter(nombre=nombre).exists()
            if(validar):
                messages.error(request, "Ya existe User Sotry con ese nombre")
            else:
                US=UserStory.objects.create(nombre=nombre,descripcion=descripcion,proyecto=proyecto)
                US.save()
                messages.success(request, "User Story Creado Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class UserStoryUpdate(View):
    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US = UserStory.objects.all()
        US2 = UserStory.objects.get(pk=pk)
        form = ProyectoUs(initial={'nombre': US2.nombre,
                                   'descripcion': US2.descripcion,
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
            nombre = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            US2.nombre = nombre
            US2.descripcion = descripcion
            US2.save()
            messages.success(request, "User Story se actualizó Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class EliminarUs(View):
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
    def get (self,request,slug,*args,**kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint=Sprint.objects.all()
        form=SprintFormCreate(slug=slug)
        context= {
            'form':form,
            'proyecto':proyecto,
            'sprint':sprint
        }
        return render  (request,'sprint/crearSprint.html',context)
    def post(self, request, slug, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        form = SprintFormCreate(request.POST,slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            US = form.cleaned_data['UserStorys']
            #duracion_estimada = form.cleaned_data['duracion_estimanda']
            validar=Sprint.objects.filter(nombre=nombre).exists()
            if(validar):
                messages.error(request, "Ya existe Sprint con ese nombre")
            else:

                sprint=Sprint.objects.create(nombre=nombre,proyecto=proyecto)
                sprint.save()
                for us in US:
                    userStory=UserStory.objects.get(nombre=us)
                    userStory.sprint=sprint
                    userStory.save()
                messages.success(request, "Sprint Creado Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('crear_sprint', slug=slug)

class ActualizarSprint(View):

    def get (self,request,slug,pk,*args,**kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint = Sprint.objects.get(pk=pk)
        form=SprintFormCreate( initial={'nombre': sprint.nombre,
                     'UserStorys': sprint.Sprint.all(),'duracion_estimanda':sprint.duracion_estimada},slug=slug)
        context= {
            'form':form,
            'proyecto':proyecto,
            'sprint':sprint
        }
        return render  (request,'sprint/actualizarSprint.html',context)

    def post(self, request,slug,pk, *args, **kwargs):
        sprint = Sprint.objects.get(pk=pk)

        form = SprintFormCreate(request.POST,slug=slug)

        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            US = form.cleaned_data['UserStorys']
            duracion_estimada = form.cleaned_data['duracion_estimanda']
            sprint.nombre=nombre
            sprint.duracion_estimada=duracion_estimada
            sprint.save()
            for us in Sprint.objects.get(pk=pk).Sprint.all():
                userStory = UserStory.objects.get(nombre=us)
                userStory.sprint=None
                userStory.save()
            for us in US:
                userStory=UserStory.objects.get(nombre=us)
                userStory.sprint=sprint
                userStory.save()

            messages.success(request, "User Story se actualizó Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('crear_sprint',slug=slug)

class listaUsSprintBacklog(View):
    def get (self,request,slug,pk,*args,**kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        sprint=Sprint.objects.get(pk=pk).Sprint.all()
       # form=SprintFormCreate(slug=slug)
        context= {
            'proyecto':proyecto,
            'US':sprint
        }
        return render  (request,'sprint_backlog/userStorySprint.html',context)



class UserStoryUpdateSprint(View):
    def get (self,request,slug,pk,*args,**kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        US=UserStory.objects.all()
        US2=UserStory.objects.get(pk=pk)
        form=AsignarDesarrolladorUs(slug=slug)
        context= {
            'form':form,
            'proyecto':proyecto,
            'US2':US2
        }
        return render  (request,'sprint_backlog/updateUsSprint.html',context)

    def post(self, request,slug,pk, *args, **kwargs):
        US2 = UserStory.objects.get(pk=pk)
        form = AsignarDesarrolladorUs(request.POST,slug=slug)
        print("asdsadsadsada",form)
        if form.is_valid():
            desarrollador=form.cleaned_data['desarrolladorAsignado']
            US2.desarrolladorAsignado=desarrollador
            US2.save()
            messages.success(request, "User Story se actualizó Correctamente!")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('sprint_backlog',slug=slug,pk=US2.sprint.pk)

