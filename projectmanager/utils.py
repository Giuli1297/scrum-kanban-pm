from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group, User, Permission


class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (text_type(user.pk))


account_activation_token = AppTokenGenerator()


def add_perm_to_group(name, permission):
    if Group.objects.filter(name=name).exists():
        group = Group.objects.get(name=name)
    else:
        group = Group.objects.create(name=name)
    group.permissions.add(Permission.objects.get(codename=permission))
    group.save()
    return group


def add_obj_perm_to_group(name, permission, instance):
    if Group.objects.filter(name=name).exists():
        group = Group.objects.get(name=name)
    else:
        group = Group.objects.create(name=name)
    assign_perm(permission, group, instance)
    group.save()
    return group


def add_user_to_obj_group(user, group_name):
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    user.save()
    return User.objects.get(id=user.id)


def remove_all_users_from_obj_group(group_name):
    group = Group.objects.get(name=group_name)
    users = User.objects.filter(groups__name=group_name)
    for user in users:
        group.user_set.remove(user)
    group.save()
    return group
