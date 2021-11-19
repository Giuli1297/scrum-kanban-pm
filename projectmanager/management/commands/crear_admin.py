import requests
from django.contrib.auth.models import Permission, Group, User
from django.core.management.base import BaseCommand, CommandError
from projectmanager.models import Rol, Proyecto, SystemActivity, UserStory, UserWorkTime, Sprint
from django.utils import timezone


class Command(BaseCommand):
    help = 'Script para crear administrador y carga de de Base de datos'
    admin = None

    def handle(self, *args, **options):
        self.crearAdministrador()

    def crearAdministrador(self):
        print("...CREAR ADMINISTRADOR.......\n\n")
        if User.objects.filter(groups__name="Administrador"):
            raise CommandError("Ya Existe Un Usuario Adminstrador")
        # admin_username = input('Ingresa el nombre de usuario: ')
        # admin_password = input('Ingresa la contraseña del administrador: ')
        # admin_email = input('Ingresa el email del administrador: ')
        admin_username = 'admin1'
        admin_password = 'admin1'
        admin_email = 'giuli1297.gg@fpuna.edu.py'

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

        try:
            self.admin = User.objects.create(username=admin_username, email=admin_email, is_staff=True,
                                             is_superuser=True)
            self.admin.set_password(admin_password)
            self.admin.save()
            admin_group = Group.objects.create(name='Administrador')
            admin_rol = Rol.objects.create(related_group=admin_group, tipo='sistema')
            for permission in Permission.objects.all():
                admin_group.permissions.add(permission)
            self.admin.groups.add(admin_group)
        except Exception as error:
            print(error)
            raise CommandError('Error intente de nuevo')
