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

from projectmanager.models.user_story_model import RegistroActividadDiairia, logHistorial
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


class UserStoryCreate(View):
    """
    Vista para crear y listar User Storys

    US
        obtiene todos los USER STORYS en el metodo get y lista los USER STORYS
    """

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
        """
        Se obtiene el proyecto en el que se está trabajando y se crea una instancia de USER STORY y se le asigna los datos correspondientes del form y tambien el proyecto
        al cual pertenece
        """
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        form = ProyectoUs(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripción_de_user_story']
            prioridad = form.cleaned_data['prioridad_1_al_10']
            documentacion = form.cleaned_data['documentación']
            if prioridad > 0 and prioridad < 11:
                US = UserStory.objects.create(descripcion=descripcion, proyecto=proyecto, prioridad=prioridad,
                                              descripcionDone=documentacion)
                US.save()
                # Log activity

                SystemActivity.objects.create(usuario=request.user,
                                              descripcion="Ha creado un user story en el proyecto " + proyecto.nombre)
                messages.success(request, "User Story Creado Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")
        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class UserStoryUpdate(View):
    """
        Vista para actualizar los datos de descripcion y prioridad de un User Story

        US
            obtiene el user story con metodo get y su pk

    """

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
        if US2.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        form = ProyectoUs(initial={
            'descripción_de_user_story': US2.descripcion,
            'prioridad_1_al_10': US2.prioridad,
            'documentación': US2.descripcionDone
        })
        context = {
            'form': form,
            'proyecto': proyecto,
            'US2': US2
        }
        return render(request, 'UserStory/UpdateUs.html', context)

    def post(self, request, slug, pk, *args, **kwargs):
        """
        Se obtiene el objeto del User Story actual y se actualiza
        con los nuevos datos de entrada
        """
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US2 = UserStory.objects.get(pk=pk)
        if US2.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        form = ProyectoUs(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripción_de_user_story']
            prioridad = form.cleaned_data['prioridad_1_al_10']
            documentacion = form.cleaned_data['documentación']
            if prioridad > 0 and prioridad < 11:
               # nuevoHistorial = HistorialUs(us=US2, descripcion=US2.descripcion, usuario=request.user,
                #                             descripcionDone=documentacion)
                #nuevoHistorial.save()
                US2.descripcion = descripcion
                US2.prioridad = prioridad
                US2.descripcionDone = documentacion

                US2.save()
                # Log activity
                logHistorial.objects.create(usuario=request.user, us=US2, descripcion="Se ha modificado el user story")
                SystemActivity.objects.create(usuario=request.user,
                                              descripcion="Ha modificado un user story en el proyecto " + proyecto.nombre)
                messages.success(request, "User Story se actualizó Correctamente!")
            else:
                messages.error(request, "Prioridad invalida, fuera del rango 1 al 10")

        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('create_us', slug=slug)


class EliminarUs(View):
    """
    Clase para eliminar un user story
    Se obtiene el objeto por su pk y se hace un delete
    """

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        if not request.user.has_perms(('projectmanager.gestionar_user_stories',),
                                      proyecto) and not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=slug)
        US = UserStory.objects.get(pk=pk)
        if US.desarrolladorAsignado:
            messages.error(request, 'User Story en sprint')
            return redirect('create_us', slug=slug)
        US.delete()
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha eliminado un user story en el proyecto " + proyecto.nombre)
        messages.success(request, "User Story Eliminado")
        return redirect('create_us', slug=slug)


class listarHistorial(View):
    """
    Vista basada en clase utilizada para mostrar el hisotrial de cambio de un User Story
    """

    def get(self, request, slug, pk):
        proyecto = Proyecto.objects.get(slug=slug)
        ustory = UserStory.objects.get(pk=pk).UsHistorial.all()
        us = UserStory.objects.get(pk=pk)
        context = {
            'history': ustory,
            'proyecto': proyecto,
            'us': us
        }
        return render(request, 'UserStory/historial.html', context)

class listarLogHistorial(View):
    """
    Vista basada en clase utilizada para mostrar el historial de cambio de un User Story
    """

    def get(self, request, slug, pk):
        proyecto = Proyecto.objects.get(slug=slug)
        ustory = UserStory.objects.get(pk=pk).logHistorial.all()
        us = UserStory.objects.get(pk=pk)
        context = {
            'history': ustory,
            'proyecto': proyecto,
            'us': us
        }
        return render(request, 'UserStory/logHistorial.html', context)

class RegistroDiario(View):
    """
    Vista basada en clase utilizada para el registro de las actividades diarias
    """

    def get(self, request, slug, pk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        US = UserStory.objects.get(pk=pk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      US) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=US.proyecto.slug)

        form = RegistroActividadForm()
        context = {
            'form': form,
            'proyecto': proyecto,
            'US': US
        }
        return render(request, 'UserStory/registroActividad.html', context)

    def post(self, request, slug, pk, *args, **kwargs):
        """
        Se obtiene el objeto del User Story actual y se actualiza
        con los nuevos datos de entrada
        """
        proyecto = Proyecto.objects.get(slug=slug)
        US = UserStory.objects.get(pk=pk)
        form = RegistroActividadForm(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripcion']
            horas = form.cleaned_data['horas']

            nuevoRegistro = RegistroActividadDiairia(us=US, descripcion=descripcion, hora=horas)

            nuevoRegistro.save()
            US.tiempoEnDesarrollo = US.tiempoEnDesarrollo + horas
            US.save()
            # Log activity
            logHistorial.objects.create(usuario=request.user, us=US, descripcion="Se ha agregado un registro de actividad al user story" )

            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha realizado un registro de actividad en el user story " + US.descripcion + " del proyecto " + proyecto.nombre)
            messages.success(request, "Se registró correctamente la actividad!")
        else:

            messages.error(request, "Un Error a ocurrido")
        return redirect('registro_actividad', slug=slug, pk=pk)


class RegistroDiarioUpdate(View):
    """
        Vista para actualizar los datos de descripcion y prioridad de un User Story

        US
            obtiene el user story con metodo get y su pk

    """

    def get(self, request, slug, pk, uspk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        user_story = UserStory.objects.get(pk=uspk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      user_story) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        registro = RegistroActividadDiairia.objects.get(pk=pk)
        form = RegistroActividadForm(initial={
            'descripcion': registro.descripcion,
            'horas': registro.hora
        })

        context = {
            'form': form,
            'proyecto': proyecto,
            'registro': registro,
        }
        return render(request, 'UserStory/registroActividadUpdate.html', context)

    def post(self, request, slug, pk, uspk, *args, **kwargs):
        """
        Se obtiene el objeto del User Story actual y se actualiza
        con los nuevos datos de entrada
        """
        proyecto = Proyecto.objects.get(slug=slug)
        US = UserStory.objects.get(pk=uspk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      US) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=US.proyecto.slug)
        registro = RegistroActividadDiairia.objects.get(pk=pk)

        US.tiempoEnDesarrollo = US.tiempoEnDesarrollo - registro.hora
        form = RegistroActividadForm(request.POST)

        if form.is_valid():
            descripcion = form.cleaned_data['descripcion']
            horas = form.cleaned_data['horas']
            registro.descripcion = descripcion
            registro.hora = horas

            registro.save()
            US.tiempoEnDesarrollo = US.tiempoEnDesarrollo + horas
            US.save()
            # Log activity
            logHistorial.objects.create(usuario=request.user, us=US,
                                        descripcion="Se ha actualizado un registro de actividad en el user story")
            SystemActivity.objects.create(usuario=request.user,
                                          descripcion="Ha realizado una actualización en el registro de actividad en el user story " + US.descripcion + " del proyecto " + proyecto.nombre)
            messages.success(request, "Registro se actualizó Correctamente!")


        else:
            messages.error(request, "Un Error a ocurrido")
        return redirect('registro_actividad', slug=slug, pk=uspk)


class RegistroDiarioDelete(View):
    """
    Clase para eliminar un registro de actividad de un user story
    Se obtiene el objeto por su pk y se hace un delete
    """

    def get(self, request, slug, pk, uspk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        user_story = UserStory.objects.get(pk=uspk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      user_story) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        registro = RegistroActividadDiairia.objects.get(pk=pk)
        US = UserStory.objects.get(pk=uspk)
        US.tiempoEnDesarrollo = US.tiempoEnDesarrollo - registro.hora
        US.save()
        registro.delete()
        logHistorial.objects.create(usuario=request.user, us=US,
                                    descripcion="Se ha eliminado un registro de actividad en el user story")
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha eliminado un registro de actividad en el user story " + US.descripcion + " del proyecto " + proyecto.nombre)
        messages.success(request, "Registro de actividad eliminado")
        return redirect('registro_actividad', slug=slug, pk=uspk)


class MarcarUSComoDoneView(View):
    """
    Vista basada en clase para la marcacion de un userstory como Done
    """

    def get(self, request, slug, usPk, *args, **kwargs):
        user_story = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.desarrollar_user_story',),
                                      user_story) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        user_story.estado = 'QA'
        user_story.save()
        # Log activity
        SystemActivity.objects.create(usuario=request.user,
                                      descripcion="Ha marcadoo como DONE es User Story " + str(user_story.pk))
        messages.success(request, "User Story marcado como done")
        return redirect('proyecto_gestion', slug=slug)


class RealizarQAUSView(View):
    """
    Vista basada en clase para la realizacion del control de calidad de un user story
    """

    def get(self, request, slug, usPk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        user_story = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.realizar_qa',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)

        form = RealizarQAUSForm()
        context = {
            'proyecto': proyecto,
            'form': form,
            'user_story': user_story
        }
        return render(request, 'UserStory/qa.html', context)

    def post(self, request, slug, usPk, *args, **kwargs):
        proyecto = Proyecto.objects.get(slug=slug)
        user_story = UserStory.objects.get(pk=usPk)
        if not request.user.has_perms(('projectmanager.realizar_qa',),
                                      proyecto) and not request.user.groups.filter(
            name='Administrador').exists():
            messages.error(request, "No tienes permisos para eso")
            return redirect('proyecto_gestion', slug=user_story.proyecto.slug)
        form = RealizarQAUSForm(request.POST)
        if form.is_valid():
            comentario = form.cleaned_data['comentario']
            aceptar = form.cleaned_data['aceptar']
            if aceptar == 'si':
                aceptar = True
            else:
                aceptar = False
            if not hasattr(user_story, 'QA'):
                QA.objects.create(comentario=comentario, aceptar=aceptar, user_story=user_story)
            else:
                qa = user_story.QA
                qa.comentario = comentario
                qa.aceptar = aceptar
                qa.save()
            if user_story.QA.aceptar:
                user_story.estado = 'Release'
            else:
                user_story.estado = 'To-Do'
                current_site = get_current_site(request)
                email_subject = 'User Story rechazado por QA.'
                email = EmailMessage(
                    email_subject,
                    'El user story con descripcion ' + user_story.descripcion + ' ha sido rechazado en QA. ' +
                    'Comentario del Scrum Master: ' + comentario,
                    EMAIL_HOST_USER,
                    [user_story.desarrolladorAsignado.email],
                )
                email.send(fail_silently=False)
            user_story.save()
            messages.success(request, "QA realizado")
            return redirect('proyecto_gestion', slug=slug)
        messages.error(request, 'Algo fue mal')
        return redirect('proyecto_gestion', slug=slug)
