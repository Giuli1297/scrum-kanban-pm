import requests
from django.contrib.auth.models import Permission, Group, User
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'CAMBIA SITE'

    def handle(self, *args, **options):
        try:
            sapp = SocialApp(provider='google', name='scrum-kanban',
                             client_id='502746393109-njpkkl1tlfrhdki9i1jkgdaitga2knic.apps.googleusercontent.com',
                             secret='Z1sNtrKMTOGMIR-UZ20vTUF5')
            sapp.save()
            site = Site.objects.all()[0]
            site.domain = '127.0.0.1:8080'
            site.name = '127.0.0.1:8080'
            site.save()
        except Exception as error:
            print(error)
            raise CommandError('Error intente de nuevo')
