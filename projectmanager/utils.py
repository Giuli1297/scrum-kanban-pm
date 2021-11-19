from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from django.contrib.auth.models import Group, User, Permission
from projectmanager.models import Rol, Proyecto 
from django.http import HttpResponse 
from django.template.loader import get_template 
from xhtml2pdf import pisa
import os
from django.conf import settings
from django.contrib.staticfiles import finders

class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.pk))


account_activation_token = AppTokenGenerator()


def add_perm_to_group(name, permission):
    if Group.objects.filter(name=name).exists():
        group = Group.objects.get(name=name)
    else:
        group = Group.objects.create(name=name)
        Rol.objects.create(related_group=group, tipo='sistema')

    group.permissions.add(Permission.objects.get(codename=permission))
    group.save()
    return group


def add_obj_perm_to_group(name, permission, instance):
    if isinstance(instance, Proyecto):
        proyecto = instance
    else:
        proyecto = instance.proyecto
    if Group.objects.filter(name=name).exists():
        group = Group.objects.get(name=name)
    else:
        group = Group.objects.create(name=name)
        if 'scrum_master' in group.name or 'scrum_member' or 'desarrollador_' in group.name:
            rol = Rol.objects.create(related_group=group, tipo='defecto', proyecto=proyecto)
        else:
            rol = Rol.objects.create(related_group=group, tipo='proyecto', proyecto=proyecto)
        rol.save()
    assign_perm(permission, group, instance)
    group.save()
    return group


def add_user_to_obj_group(user, group_name):
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()
    return User.objects.get(id=user.id)


def add_users_to_obj_group(users, group_name):
    for user in users:
        print(user.username)
        add_user_to_obj_group(user, group_name)
    return


def remove_all_users_from_obj_group(group_name):
    group = Group.objects.get(name=group_name)
    users = User.objects.filter(groups__name=group_name)
    for user in users:
        group.user_set.remove(user)
    group.save()
    return group


def remove_all_perms_from_obj_group(group_name, instance):
    group = Group.objects.get(name=group_name)
    for perm in get_perms(group, instance):
        remove_perm(perm, group, instance)
    group.save()
    return group


def calcular_capacidad_desarrollador(sm, proyecto):
    capacidad = 0
    for user_work in sm.tiempos_de_trabajo.all():
        if user_work.proyecto == proyecto:
            capacidad += user_work.horas
    return capacidad 


def render_to_pdf(template_origen, contexto):
    response = HttpResponse(content_type='application/pdf')
    template = get_template(template_origen)
    html = template.render(contexto)
    
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)

    if pisa_status.err:
       return HttpResponse('Hubo un error <pre>' + html + '</pre>')
    return response


def link_callback(uri, rel):
    """
    Convertir los URIs de HTML en rutas absolutas del sistema para que xhtml2pdf 
    pueda acceder a esos recursos.
    """
    result = finders.find(uri)
    if result:
            if not isinstance(result, (list, tuple)):
                    result = [result]
            result = list(os.path.realpath(path) for path in result)
            path=result[0]
    else:
            sUrl = settings.STATIC_URL        # Typically /static/
            sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
            mUrl = settings.MEDIA_URL         # Typically /media/
            mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media
            if uri.startswith(mUrl):
                    path = os.path.join(mRoot, uri.replace(mUrl, ""))
            elif uri.startswith(sUrl):
                    path = os.path.join(sRoot, uri.replace(sUrl, ""))
            else:
                    return ur
    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                    'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path