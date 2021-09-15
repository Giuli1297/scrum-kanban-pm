from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from scrum_kanban_pm.settings.development import EMAIL_HOST_USER
from django.db.models.signals import post_save, m2m_changed
from django.db import transaction
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from .utils import account_activation_token
from django.urls import reverse
from .models import Proyecto
from .utils import add_obj_perm_to_group, add_user_to_obj_group, add_perm_to_group, remove_all_users_from_obj_group, \
    add_users_to_obj_group


@receiver(user_signed_up)
def send_email_to_admin(request, user, **kwargs):
    admin = User.objects.get(groups__name='Administrador')
    user.is_active = False
    user.save()
    current_site = get_current_site(request)
    email_body = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    }

    link = reverse('activate', kwargs={
        'uidb64': email_body['uid'], 'token': email_body['token']})

    email_subject = 'Usuario nuevo registrado'

    activate_url = 'http://' + current_site.domain + link

    email = EmailMessage(
        email_subject,
        'El usuario ' + user.username + 'se ha registrado, \n Activar Cuenta: \n' + activate_url,
        EMAIL_HOST_USER,
        [admin.email],
    )
    email.send(fail_silently=False)


@receiver(post_save, sender=Proyecto)
def add_scrum_master_signal(sender, instance, created, **kwargs):
    if created:
        # Scrum Master Handler
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'editar_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'ver_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'iniciar_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'crear_roles_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'ver_roles_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'importar_roles_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'modificar_roles_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'eliminar_roles_proyecto', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'agregar_smember', instance)
        add_obj_perm_to_group('scrum_master_' + instance.slug, 'crear_user_stories', instance)
        add_perm_to_group('scrum_master_' + instance.slug, 'ver_proyectos')
        add_user_to_obj_group(instance.scrum_master, 'scrum_master_' + instance.slug)
        add_obj_perm_to_group('scrum_member_' + instance.slug, 'ver_proyecto', instance)
        add_perm_to_group('scrum_member_' + instance.slug, 'ver_proyectos')

        # Admin Handler
        add_obj_perm_to_group('Administrador', 'editar_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'ver_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'iniciar_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'crear_roles_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'ver_roles_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'importar_roles_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'modificar_roles_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'eliminar_roles_proyecto', instance)
        add_obj_perm_to_group('Administrador', 'agregar_smember', instance)
        add_obj_perm_to_group('Administrador', 'crear_user_stories', instance)
    else:
        remove_all_users_from_obj_group('scrum_master_' + instance.slug)
        add_user_to_obj_group(instance.scrum_master, 'scrum_master_' + instance.slug)


@receiver(m2m_changed, sender=Proyecto.scrum_member.through)
def add_scrum_members_signal(sender, instance, **kwargs):
    remove_all_users_from_obj_group('scrum_member_' + instance.slug)
    print(instance.scrum_member.all())
    add_users_to_obj_group(instance.scrum_member.all(), 'scrum_member_' + instance.slug)
