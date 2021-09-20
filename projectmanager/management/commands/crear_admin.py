import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.core.management.base import BaseCommand, CommandError
from projectmanager.models import Rol


class Command(BaseCommand):
    help = 'Crea un usuario administrador con todos los permisos'

    def handle(self, *args, **options):
        if User.objects.filter(groups__name="Administrador"):
            raise CommandError("Ya Existe Un Usuario Adminstrador")
        admin_username = input('Ingresa el nombre de usuario: ')
        admin_password = input('Ingresa la contrasena del administrador: ')

        admin_nombre = input('Ingresa el nombre del administrador: ')
        admin_apellido = input('Ingresa el apellido del administrador: ')

        """
        while True:
            response = requests.get(
                "https://isitarealemail.com/api/email/validate",
                params={'email': admin_email}
            )

            status = response.json()['status']
            if status == "valid":
                break
            else:
                admin_email = input("El email es invalido o no existe, vuelva a ingresarlo: ")
        """

        try:
            User = get_user_model()
            admin = User.objects.create_superuser(admin_email, admin_nombre, admin_apellido, admin_password)
            admin_group = Group.objects.create(name='Administrador')
            admin_rol = Rol.objects.create(related_group=admin_group, tipo='sistema')
            for permission in Permission.objects.all():
                admin_group.permissions.add(permission)
            admin.groups.add(admin_group)
        except Exception as error:
            print(error)
            raise CommandError('Error intente de nuevo')
