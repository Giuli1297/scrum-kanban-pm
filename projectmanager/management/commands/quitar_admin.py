import requests
from django.contrib.auth.models import Permission, Group, User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Remueve al usuario administrador'

    def handle(self, *args, **options):
        if not User.objects.filter(groups__name="Administrador"):
            raise CommandError("No Existe Un Usuario Adminstrador")
        try:
            admin = User.objects.get(groups__name="Administrador")
            admin.delete()
            Group.objects.get(name="Administrador").delete()
        except Exception as error:
            print(error)
            raise CommandError('Error intente de nuevo')
