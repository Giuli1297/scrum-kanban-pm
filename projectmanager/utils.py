from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from guardian.shortcuts import assign_perm, remove_perm, get_perms
from django.contrib.auth.models import Group, User, Permission
from projectmanager.models import Rol, Proyecto


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
