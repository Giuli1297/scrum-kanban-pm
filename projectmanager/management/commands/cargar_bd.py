import requests
from django.contrib.auth.models import Permission, Group, User
from django.core.management.base import BaseCommand, CommandError
from projectmanager.models import Rol, Proyecto, SystemActivity, UserStory, UserWorkTime, Sprint
from django.utils import timezone

# Lista de usuarios iniciales
usuarios = [
    {'username': "juan"},
    {'username': "marcelo"},
    {'username': "jessica"},
    {'username': "juana"},
    {'username': "nelson"},
    {'username': "cesar"},
    {'username': "ivan"},
    {'username': "mariela"},
    {'username': "claudia"},
    {'username': "ronaldo"},
    {'username': "araceli"},
    {'username': "nahuel"},
    {'username': "carlos"},
    {'username': "mirian"},
    {'username': "moreno"},
    {'username': "roberto"},
    {'username': "marta"},
    {'username': "alex"},
    {'username': "carla"},
    {'username': "martin"},
    {'username': "lionel"},
    {'username': "machuca"},
    {'username': "esteban"},
    {'username': "marcela"},
    {'username': "ara"}
]

# Scrum members a a proyectos
sm = [
    {
        'proyecto': "proyecto1",
        'miembros': ["juan", "juana", "nelson", "cesar"]
    },
    {
        'proyecto': "proyecto2",
        'miembros': ["mariela", "ronaldo", "araceli", "carlos"]
    },
    {
        'proyecto': "proyecto3",
        'miembros': ["mirian", "moreno", "roberto", "marta"]
    },
    {
        'proyecto': "proyecto4",
        'miembros': ["carla", "martin", "lionel", "machuca"]
    },
    {
        'proyecto': "proyecto5",
        'miembros': ["esteban", "marcela", "ara", "alex"]
    }
]

# Lista de proyectos iniciales
proyectos = [
    {'nombre': "Proyecto1", 'descripcion': "Primer proyecto", 'scrum_master': 'ivan'},
    {'nombre': "Proyecto2", 'descripcion': "Segundo proyecto", 'scrum_master': 'jessica'},
    {'nombre': "Proyecto3", 'descripcion': "Tercer proyecto", 'scrum_master': 'nahuel'},
    {'nombre': "Proyecto4", 'descripcion': "Cuarto proyecto", 'scrum_master': 'claudia'},
    {'nombre': "Proyecto5", 'descripcion': "Quinto proyecto", 'scrum_master': 'marcelo'}
]

userHistory = [
    {
        'proyecto': "proyecto1",
        'us': [
            {'descripcion': "US1_P1", "requisitos": "Terminar y testear el server", "prioridad": 1},
            {'descripcion': "US2_P1", "requisitos": "Terminar y testear el server", "prioridad": 2},
            {'descripcion': "US3_P1", "requisitos": "Terminar y testear el server", "prioridad": 3},
            {'descripcion': "US4_P1", "requisitos": "Terminar y testear el server", "prioridad": 5},
            {'descripcion': "US5_P1", "requisitos": "Terminar y testear el server", "prioridad": 4},
            {'descripcion': "US6_P1", "requisitos": "Terminar y testear el server", "prioridad": 7},
        ]
    },
    {
        'proyecto': "proyecto2",
        'us': [
            {'descripcion': "US1_P2", "requisitos": "Terminar y testear el server", "prioridad": 1},
            {'descripcion': "US2_P2", "requisitos": "Terminar y testear el server", "prioridad": 2},
            {'descripcion': "US3_P2", "requisitos": "Terminar y testear el server", "prioridad": 3},
            {'descripcion': "US4_P2", "requisitos": "Terminar y testear el server", "prioridad": 5},
            {'descripcion': "US5_P2", "requisitos": "Terminar y testear el server", "prioridad": 4},
            {'descripcion': "US6_P2", "requisitos": "Terminar y testear el server", "prioridad": 7},
        ]
    },
    {
        'proyecto': "proyecto3",
        'us': [
            {'descripcion': "US1_P3", "requisitos": "Terminar y testear el server", "prioridad": 1},
            {'descripcion': "US2_P3", "requisitos": "Terminar y testear el server", "prioridad": 2},
            {'descripcion': "US3_P3", "requisitos": "Terminar y testear el server", "prioridad": 3},
            {'descripcion': "US4_P3", "requisitos": "Terminar y testear el server", "prioridad": 5},
            {'descripcion': "US5_P3", "requisitos": "Terminar y testear el server", "prioridad": 4},
            {'descripcion': "US6_P3", "requisitos": "Terminar y testear el server", "prioridad": 7},
        ]
    },
    {
        'proyecto': "proyecto4",
        'us': [
            {'descripcion': "US1_P4", "requisitos": "Terminar y testear el server", "prioridad": 1},
            {'descripcion': "US2_P4", "requisitos": "Terminar y testear el server", "prioridad": 2},
            {'descripcion': "US3_P4", "requisitos": "Terminar y testear el server", "prioridad": 3},
            {'descripcion': "US4_P4", "requisitos": "Terminar y testear el server", "prioridad": 5},
            {'descripcion': "US5_P4", "requisitos": "Terminar y testear el server", "prioridad": 4},
            {'descripcion': "US6_P4", "requisitos": "Terminar y testear el server", "prioridad": 7},
        ]
    },
    {
        'proyecto': "proyecto5",
        'us': [
            {'descripcion': "US1_P5", "requisitos": "Terminar y testear el server", "prioridad": 1},
            {'descripcion': "US2_P5", "requisitos": "Terminar y testear el server", "prioridad": 2},
            {'descripcion': "US3_P5", "requisitos": "Terminar y testear el server", "prioridad": 3},
            {'descripcion': "US4_P5", "requisitos": "Terminar y testear el server", "prioridad": 5},
            {'descripcion': "US5_P5", "requisitos": "Terminar y testear el server", "prioridad": 4},
            {'descripcion': "US6_P5", "requisitos": "Terminar y testear el server", "prioridad": 7},
        ]
    }
]


class Command(BaseCommand):
    help = 'Script para crear administrador y carga de de Base de datos'
    admin = None

    def handle(self, *args, **options):
        self.crearUsuarios()
        self.crearProyectos()
        self.crearUSPorProyecto()
        self.agregarSM_A_Proyecto()
        self.crear_proyecto_iniciado()

    def crearUsuarios(self):
        print("...CREACION DE USUARIOS....\n\n")
        for usuario in usuarios:
            user = User.objects.create(username=usuario['username'], email="jperezis2fpuna@gmail.com")
            user.set_password("Probando1")
            user.save() 
        self.admin = User.objects.get(is_superuser=True)

    def crearProyectos(self):
        print("...CREACION DE PROYECTOS....\n\n")
        for proyecto in proyectos:
            Proyecto.objects.create(nombre=proyecto['nombre'], descripcion=proyecto['descripcion'],
                                    scrum_master=User.objects.get(username=proyecto['scrum_master']))
            SystemActivity.objects.create(usuario=self.admin,
                                          descripcion="Ha creado el " + proyecto['nombre'])

    def crearUSPorProyecto(self):
        print("...CREACION DE US POR PROYECTOS....\n\n")
        for x in userHistory:
            p = Proyecto.objects.get(nombre=x['proyecto'])
            for y in x['us']:
                UserStory.objects.create(descripcion=y['descripcion'], descripcionDone=y['requisitos'], prioridad=y['prioridad'] proyecto=p)
                SystemActivity.objects.create(usuario=self.admin,
                                              descripcion="Ha creado un user story en el proyecto " + x['proyecto'])

    def agregarSM_A_Proyecto(self):
        print("...AGREGAR SCRUM_MEMBERS A PROYECTOS....\n\n")
        for x in sm:
            p = Proyecto.objects.get(nombre=x['proyecto'])
            for y in x['miembros']:
                u = User.objects.get(username=y)
                UserWorkTime.objects.create(proyecto=p, desarrollador=u, dia='LUN', horas=5, totalEnProyecto=25)
                UserWorkTime.objects.create(proyecto=p, desarrollador=u, dia='MAR', horas=5, totalEnProyecto=25)
                UserWorkTime.objects.create(proyecto=p, desarrollador=u, dia='MIE', horas=5, totalEnProyecto=25)
                UserWorkTime.objects.create(proyecto=p, desarrollador=u, dia='JUE', horas=5, totalEnProyecto=25)
                UserWorkTime.objects.create(proyecto=p, desarrollador=u, dia='VIE', horas=5, totalEnProyecto=25)
                p.scrum_member.add(u)
                p.save()
                SystemActivity.objects.create(usuario=self.admin,
                                              descripcion="Ha agregado Scrum Members al proyecto " + x['proyecto'])

    def crear_proyecto_iniciado(self):
        pr = Proyecto.objects.create(nombre='Proyecto Iniciado', descripcion='Test',
                                     scrum_master=User.objects.get(username='marcelo'), estado='ACT',
                                     fecha_inicio=timezone.now() - timezone.timedelta(days=20))
        user = User.objects.get(username='ivan')
        adminuser = User.objects.filter(groups__name="Administrador")[0]
        UserWorkTime.objects.create(proyecto=pr, desarrollador=user, dia='LUN', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=user, dia='MAR', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=user, dia='MIE', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=user, dia='JUE', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=user, dia='VIE', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=adminuser, dia='LUN', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=adminuser, dia='MAR', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=adminuser, dia='MIE', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=adminuser, dia='JUE', horas=5, totalEnProyecto=25)
        UserWorkTime.objects.create(proyecto=pr, desarrollador=adminuser, dia='VIE', horas=5, totalEnProyecto=25)
        pr.scrum_member.add(user)
        pr.scrum_member.add(adminuser)
        sprint = Sprint.objects.create(fecha_inicio=timezone.now() - timezone.timedelta(days=19),
                                       fecha_inicio_desarrollo=timezone.now() - timezone.timedelta(days=15),
                                       duracion_estimada_dias=20,
                                       estado='conf3',
                                       proyecto=pr,
                                       proyecto_actual=pr)
        us1 = UserStory(descripcion='US1', tiempoEstimado=18.5, estado='To-Do', desarrolladorAsignado=user,
                        proyecto=pr, sprint=sprint, prioridad=5, descripcionDone="test")
        us2 = UserStory(descripcion='US2', tiempoEstimado=18.5, estado='To-Do', desarrolladorAsignado=adminuser,
                        proyecto=pr, sprint=sprint, prioridad=5, descripcionDone="test")
        us3 = UserStory(descripcion='US3', tiempoEstimado=18.5, estado='To-Do', desarrolladorAsignado=user,
                        proyecto=pr, sprint=sprint, prioridad=5, descripcionDone="test")
        us4 = UserStory(descripcion='US4', tiempoEstimado=18.5, estado='To-Do', desarrolladorAsignado=adminuser,
                        proyecto=pr, sprint=sprint, prioridad=5, descripcionDone="test")
        us5 = UserStory(descripcion='US5', tiempoEstimado=18.5, estado='To-Do', desarrolladorAsignado=user,
                        proyecto=pr, sprint=sprint, prioridad=5, descripcionDone="test")
        us1.save()
        us2.save()
        us3.save()
        us4.save()
        us5.save()
        pr.save()
