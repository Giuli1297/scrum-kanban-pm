from datetime import datetime, timedelta

import numpy
import pytz
import requests
from django.contrib.auth.models import Permission, Group, User
from django.core.management.base import BaseCommand, CommandError
from projectmanager.models import Rol, Proyecto, SystemActivity, UserStory, UserWorkTime, Sprint, CapacidadSMasteSprint, \
    QA
from django.utils import timezone

from projectmanager.models.user_story_model import RegistroActividadDiairia, UserStorySprint
from projectmanager.utils import add_obj_perm_to_group, add_user_to_obj_group

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

# Lista de proyectos iniciales
proyectos = [
    {'nombre': "Proyecto Cancelado", 'descripcion': "Primer proyecto",
     'scrum_master': 'ivan', 'fecha_inicio': '2021-01-05', 'estado': 'CAN', 'fecha_fin': '2021-01-06'},
    {'nombre': "Proyecto Pendiente", 'descripcion': "Segundo proyecto",
     'scrum_master': 'jessica', 'fecha_inicio': '2021-11-02', 'estado': 'PEN', 'fecha_fin': None},
    {'nombre': "Proyecto Planificando", 'descripcion': "Tercer proyecto",
     'scrum_master': 'nahuel', 'fecha_inicio': '2021-11-08', 'estado': 'ACT', 'fecha_fin': None},
    {'nombre': "Proyecto 1Sfin1SEje1Plan", 'descripcion': "Quinto proyecto",
     'scrum_master': 'marcelo', 'fecha_inicio': '2021-11-01', 'estado': 'ACT', 'fecha_fin': None},
    {'nombre': "Proyecto Finalizado", 'descripcion': "Quinto proyecto",
     'scrum_master': 'jessica', 'fecha_inicio': '2021-08-12', 'estado': 'ACT', 'fecha_fin': '2021-08-31'}

]

sm = [
    {
        'proyecto': "proyecto-cancelado",
        'miembros': ["juan", "juana", "nelson", "cesar"]
    },
    {
        'proyecto': "proyecto-pendiente",
        'miembros': ["mariela", "ronaldo", "araceli", "carlos"]
    },
    {
        'proyecto': "proyecto-planificando",
        'miembros': ["mirian", "moreno", "roberto", "marta"]
    },
    {
        'proyecto': "proyecto-finalizado",
        'miembros': ["carla", "martin", "lionel", "machuca"]
    },
    {
        'proyecto': "proyecto-1sfin1seje1plan",
        'miembros': ["admin1", "marcela", "ara", "alex"]
    }
]

userHistory = [
    {
        'proyecto': "proyecto-cancelado",
        'us': [
            {'descripcion': "US1_P1", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US2_P1", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US3_P1", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US4_P1", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US5_P1", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US6_P1", "requisitos": "Terminar y testear el server"},
        ]
    },
    {
        'proyecto': "proyecto-pendiente",
        'us': [
            {'descripcion': "US1_P2", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US2_P2", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US3_P2", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US4_P2", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US5_P2", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US6_P2", "requisitos": "Terminar y testear el server"},
        ]
    },
    {
        'proyecto': "proyecto-planificando",
        'us': [
            {'descripcion': "US1_P3", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US2_P3", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US3_P3", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US4_P3", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US5_P3", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US6_P3", "requisitos": "Terminar y testear el server"},
        ]
    },
    {
        'proyecto': "proyecto-finalizado",
        'us': [
            {'descripcion': "US1_P4", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US2_P4", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US3_P4", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US4_P4", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US5_P4", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US6_P4", "requisitos": "Terminar y testear el server"},
        ]
    },
    {
        'proyecto': "proyecto-1sfin1seje1plan",
        'us': [
            {'descripcion': "US1_P5", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US2_P5", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US3_P5", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US4_P5", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US5_P5", "requisitos": "Terminar y testear el server"},
            {'descripcion': "US6_P5", "requisitos": "Terminar y testear el server"},
        ]
    }
]


class Command(BaseCommand):
    help = 'Script para crear administrador y carga de de Base de datos'
    admin = None
    capacidad_dev = {}

    def handle(self, *args, **options):
        self.crearUsuarios()
        self.crearProyectos()
        self.agregarSM_A_Proyecto()
        self.crearUSPorProyecto()
        self.configuar_proyecto_planificando()
        self.configurar_proyecto_iniciado()
        self.configurar_proyecto_finalizado()

    def crearUsuarios(self):
        print("...CREACION DE USUARIOS....\n\n")
        for usuario in usuarios:
            user = User.objects.create(username=usuario['username'], email="jperezis2fpuna@gmail.com")
            user.set_password("test")
            user.save()
        self.admin = User.objects.get(groups__name='Administrador')

    def crearProyectos(self):
        print("...CREACION DE PROYECTOS....\n\n")
        asuncion = pytz.timezone('America/Asuncion')
        for proyecto in proyectos:
            Proyecto.objects.create(nombre=proyecto['nombre'], descripcion=proyecto['descripcion'],
                                    scrum_master=User.objects.get(username=proyecto['scrum_master']),
                                    estado=proyecto['estado'],
                                    fecha_inicio=asuncion.localize(
                                        datetime.strptime(proyecto['fecha_inicio'], "%Y-%m-%d")),
                                    fecha_fin=asuncion.localize(
                                        datetime.strptime(proyecto['fecha_inicio'], "%Y-%m-%d")))
            SystemActivity.objects.create(usuario=self.admin,
                                          descripcion="Ha creado el " + proyecto['nombre'])

    def agregarSM_A_Proyecto(self):
        print("...AGREGAR SCRUM_MEMBERS A PROYECTOS....\n\n")
        for x in sm:
            p = Proyecto.objects.get(slug=x['proyecto'])
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

    def configuar_proyecto_planificando(self):
        asuncion = pytz.timezone('America/Asuncion')
        proyecto = Proyecto.objects.get(slug='proyecto-planificando')
        fecha_inicio_sprint = asuncion.localize(datetime.strptime('2021-11-19', "%Y-%m-%d"))
        fecha_fin_sprint = asuncion.localize(datetime.strptime('2021-11-24', "%Y-%m-%d"))
        fecha_inicio_sprint_siguiente = asuncion.localize(datetime.strptime('2021-11-25', "%Y-%m-%d"))
        fecha_fin_sprint_siguiente = asuncion.localize(datetime.strptime('2021-11-30', "%Y-%m-%d"))
        sprint_actual = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint,
            fecha_finalizacion=fecha_fin_sprint,
            fecha_inicio_desarrollo=fecha_inicio_sprint, fecha_finalizacion_real=fecha_fin_sprint,
            proyecto=proyecto,
            proyecto_actual=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint, fecha_fin_sprint)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_actual, scrum_member=s_member)
            sprint_actual.scrum_member.add(s_member)
        sprint_actual.save()

        sprint_siguiente = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint_siguiente,
            fecha_finalizacion=fecha_fin_sprint_siguiente,
            fecha_inicio_desarrollo=fecha_inicio_sprint_siguiente, fecha_finalizacion_real=fecha_fin_sprint_siguiente,
            proyecto=proyecto,
            proyecto_sig=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_siguiente,
                                                           fecha_fin_sprint_siguiente)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_siguiente, scrum_member=s_member)
            sprint_siguiente.scrum_member.add(s_member)
        sprint_siguiente.save()

    # {'nombre': "Proyecto 1Sfin1SEje1Plan", 'descripcion': "Quinto proyecto",
    #  'scrum_master': 'marcelo', 'fecha_inicio': '2021-11-01', 'estado': 'ACT', 'fecha_fin': None},
    def configurar_proyecto_iniciado(self):
        asuncion = pytz.timezone('America/Asuncion')
        proyecto = Proyecto.objects.get(slug='proyecto-1sfin1seje1plan')
        fecha_inicio_sprint_fin = asuncion.localize(datetime.strptime('2021-11-01', "%Y-%m-%d"))
        fecha_fin_sprint_fin = asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d"))
        fecha_inicio_sprint_eje = asuncion.localize(datetime.strptime('2021-11-15', "%Y-%m-%d"))
        fecha_fin_sprint_eje = asuncion.localize(datetime.strptime('2021-11-22', "%Y-%m-%d"))
        fecha_inicio_sprint_plan = asuncion.localize(datetime.strptime('2021-11-23', "%Y-%m-%d"))
        fecha_fin_sprint_plan = asuncion.localize(datetime.strptime('2021-11-30', "%Y-%m-%d"))

        # Sprint Finalizado
        #
        # Creacion
        sprint_fin = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint_fin,
            fecha_finalizacion=fecha_fin_sprint_fin,
            fecha_inicio_desarrollo=fecha_inicio_sprint_fin, fecha_finalizacion_real=fecha_fin_sprint_fin,
            proyecto=proyecto,
            proyecto_actual=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_fin, fecha_fin_sprint_fin)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_fin, scrum_member=s_member)
            sprint_fin.scrum_member.add(s_member)
        sprint_fin.save()
        # Carga de Sprint Backlog
        us = proyecto.product_backlog.all().order_by('id')
        u_1 = us[1]
        u_2 = us[2]
        u_3 = us[3]
        u_1.sprint = sprint_fin
        u_1.save()
        u_2.sprint = sprint_fin
        u_2.save()
        u_3.sprint = sprint_fin
        u_3.save()
        #

        # Planificar User Stories
        de = proyecto.scrum_member.all().order_by('id')
        d_1 = de[1]
        d_2 = de[2]
        d_3 = de[3]
        u_1.desarrolladorAsignado = d_1
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se asigno al desarrolador " + d_1.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_2.desarrolladorAsignado = d_2
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se asigno al desarrolador " + d_2.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_3.desarrolladorAsignado = d_3
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se asigno al desarrolador " + d_3.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_1.tiempoEstimadoSMaster = 20
        u_2.tiempoEstimadoSMaster = 20
        u_3.tiempoEstimadoSMaster = 20
        sprint_fin.horas_ocupadas_us += 60
        cap1 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_1)
        cap2 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_2)
        cap3 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_3)
        cap1.saldo_horas -= 20
        cap2.saldo_horas -= 20
        cap3.saldo_horas -= 20
        add_obj_perm_to_group('desarrollador_de_' + str(u_1.pk), 'desarrollar_user_story', u_1)
        add_user_to_obj_group(d_1, 'desarrollador_de_' + str(u_1.pk))
        add_obj_perm_to_group('desarrollador_de_' + str(u_2.pk), 'desarrollar_user_story', u_2)
        add_user_to_obj_group(d_2, 'desarrollador_de_' + str(u_2.pk))
        add_obj_perm_to_group('desarrollador_de_' + str(u_3.pk), 'desarrollar_user_story', u_3)
        add_user_to_obj_group(d_3, 'desarrollador_de_' + str(u_3.pk))
        d_1.save()
        d_2.save()
        d_3.save()
        u_1.save()
        u_2.save()
        u_3.save()
        cap1.save()
        cap2.save()
        cap3.save()
        sprint_fin.save()

        # Planning Poker
        sprint_fin.estado = 'conf2'
        sprint_fin.save()
        u_1.tiempoEstimado = 20
        u_2.tiempoEstimado = 20
        u_3.tiempoEstimado = 20
        u_1.save()
        u_2.save()
        u_3.save()

        # Inicio desarrollo
        sprint_fin.fecha_inicio_desarrollo = fecha_inicio_sprint_fin
        sprint_fin.duracion_estimada_dias = numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                               sprint_fin.fecha_finalizacion_real.date())
        sprint_fin.estado = 'conf3'
        u_1.estado = 'Doing'
        u_2.estado = 'Doing'
        u_3.estado = 'Doing'
        u_1.save()
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se paso Doing",
                                                fecha=fecha_inicio_sprint_fin)
        u_2.save()
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se paso Doing",
                                                fecha=fecha_inicio_sprint_fin)
        u_3.save()
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se paso Doing",
                                                fecha=fecha_inicio_sprint_fin)
        sprint_fin.save()

        # Registrar Actividades
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-02', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-04', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-08', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-09', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-03', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-05', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-09', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-03', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-04', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-08', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        u_1.tiempoEnDesarrollo = 20
        u_2.tiempoEnDesarrollo = 20
        u_3.tiempoEnDesarrollo = 20
        u_1.save()
        u_2.save()
        u_3.save()

        # Marcar como done
        QA.objects.create(comentario="comentario", aceptar=True, user_story=u_1,
                          fecha=asuncion.localize(datetime.strptime('2021-11-09', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se acepto en QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-11-09', "%Y-%m-%d")))
        QA.objects.create(comentario="comentario1", aceptar=True, user_story=u_2,
                          fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se acepto en QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        QA.objects.create(comentario="comentario2", aceptar=False, user_story=u_3,
                          fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se rechazo en QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-11-10', "%Y-%m-%d")))
        u_1.estado = 'Release'
        u_2.estado = 'Release'
        u_3.estado = 'QA'
        u_1.save()
        u_2.save()
        u_3.save()

        # Finalizar Sprint
        registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint_fin)
        horas_us_total = 0
        for us in sprint_fin.sprint_backlog.all():
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint_fin.duracion_estimada_dias
        progreso = []
        progreso_act = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
            progreso_act.append(horas_us_total)
        for us in sprint_fin.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                print(sprint_fin.fecha_inicio_desarrollo.date())
                print(us.QA.fecha.date())
                print(diferencia_dia)
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0

        for actividad in registros_de_actividad:
            if actividad.sprint == sprint_fin and actividad.hora > 0:
                diferencia_dia = int(numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                        actividad.fecha.date()))
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso_act[(duracionSprint) - i] -= actividad.hora
        passed_days = duracionSprint
        sprint_fin.saved_us_progress = progreso
        sprint_fin.saved_act_progress = progreso_act
        sprint_fin.saved_horas_us_total = horas_us_total
        sprint_fin.fecha_finalizacion_real = sprint_fin.fecha_finalizacion
        sprint_fin.proyecto_actual = None
        sprint_fin.save()
        ##
        sprint_actual = sprint_fin
        sprint_sig = None
        ##
        if sprint_actual.estado == 'conf3':
            sprint_actual.estado = 'fin'
            for user_story in sprint_actual.sprint_backlog.all():
                if user_story.estado != 'Release':
                    user_story.estado = 'no-terminado'
                    user_story.desarrolladorAsignado = None
                    user_story.save()
            sprint_actual.proyecto_actual = None
            sprint_actual.fecha_finalizacion_real = sprint_fin.fecha_finalizacion
            sprint_actual.save()
            if hasattr(proyecto, "siguiente_sprint"):
                if proyecto.siguiente_sprint is not None:
                    sprint_sig.proyecto_actual = proyecto
                    sprint_sig.proyecto_sig = None
                    sprint_sig.save()
            proyecto.save()
            for us in sprint_fin.sprint_backlog.all():
                newUs = UserStorySprint.objects.create(descripcion=us.descripcion,
                                                       tiempoEstimadoSMaster=us.tiempoEstimadoSMaster,
                                                       tiempoEstimado=us.tiempoEstimado, estado=us.estado,
                                                       tiempoEnDesarrollo=us.tiempoEnDesarrollo, proyecto=us.proyecto,
                                                       sprintUs=us.sprint,
                                                       prioridad=us.prioridad, descripcionDone=us.descripcionDone,
                                                       desarrolladorAsignado=us.desarrolladorAsignado)
                for act in us.RegistroActividad.all():
                    RegistroActividadDiairia.objects.create(us2=newUs, descripcion=act.descripcion, fecha=act.fecha,
                                                            hora=act.hora)

        # Speint en proceso y planificado
        # Planificacion
        sprint_eje = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint_eje,
            fecha_finalizacion=fecha_fin_sprint_eje,
            fecha_inicio_desarrollo=fecha_inicio_sprint_eje, fecha_finalizacion_real=fecha_fin_sprint_eje,
            proyecto=proyecto,
            proyecto_actual=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_eje, fecha_fin_sprint_eje)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_eje, scrum_member=s_member)
            sprint_eje.scrum_member.add(s_member)
        sprint_eje.save()
        sprint_plan = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint_plan,
            fecha_finalizacion=fecha_fin_sprint_plan,
            fecha_inicio_desarrollo=fecha_inicio_sprint_plan, fecha_finalizacion_real=fecha_fin_sprint_plan,
            proyecto=proyecto,
            proyecto_sig=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_plan, fecha_fin_sprint_plan)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_plan, scrum_member=s_member)
            sprint_plan.scrum_member.add(s_member)
        sprint_plan.save()
        # Carga de Sprint Backlog
        us = proyecto.product_backlog.all().order_by('id')
        u_1 = us[4]
        u_2 = us[5]
        u_1.sprint = sprint_eje
        u_1.save()
        u_2.sprint = sprint_eje
        u_2.save()
        #

        # Planificar User Stories
        de = proyecto.scrum_member.all().order_by('id')
        d_1 = de[0]
        d_2 = de[3]
        u_1.desarrolladorAsignado = d_1
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se asigno al desarrolador " + d_1.username,
                                                fecha=fecha_inicio_sprint_eje)
        u_2.desarrolladorAsignado = d_2
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se asigno al desarrolador " + d_2.username,
                                                fecha=fecha_inicio_sprint_eje)
        u_1.tiempoEstimadoSMaster = 20
        u_2.tiempoEstimadoSMaster = 20
        sprint_eje.horas_ocupadas_us += 40
        cap1 = CapacidadSMasteSprint.objects.get(sprint=sprint_eje, scrum_member=d_1)
        cap2 = CapacidadSMasteSprint.objects.get(sprint=sprint_eje, scrum_member=d_2)
        cap1.saldo_horas -= 20
        cap2.saldo_horas -= 20
        add_obj_perm_to_group('desarrollador_de_' + str(u_1.pk), 'desarrollar_user_story', u_1)
        add_user_to_obj_group(d_1, 'desarrollador_de_' + str(u_1.pk))
        add_obj_perm_to_group('desarrollador_de_' + str(u_2.pk), 'desarrollar_user_story', u_2)
        add_user_to_obj_group(d_2, 'desarrollador_de_' + str(u_2.pk))
        d_1.save()
        d_2.save()
        u_1.save()
        u_2.save()
        cap1.save()
        cap2.save()
        sprint_eje.save()

        # Planning Poker
        sprint_eje.estado = 'conf2'
        sprint_eje.save()
        u_1.tiempoEstimado = 20
        u_2.tiempoEstimado = 20
        u_1.save()
        u_2.save()

        # Inicio desarrollo
        sprint_eje.fecha_inicio_desarrollo = fecha_inicio_sprint_eje
        sprint_eje.duracion_estimada_dias = numpy.busday_count(sprint_eje.fecha_inicio_desarrollo.date(),
                                                               sprint_eje.fecha_finalizacion_real.date())
        sprint_eje.estado = 'conf3'
        u_1.estado = 'To-Do'
        u_2.estado = 'To-Do'
        u_1.save()
        u_2.save()
        sprint_eje.save()

    # {'nombre': "Proyecto Finalizado", 'descripcion': "Quinto proyecto",
    #  'scrum_master': 'jessica', 'fecha_inicio': '2021-08-12', 'estado': 'FIN', 'fecha_fin': '2021-08-31'}
    def configurar_proyecto_finalizado(self):
        asuncion = pytz.timezone('America/Asuncion')
        proyecto = Proyecto.objects.get(slug='proyecto-finalizado')
        fecha_inicio_sprint_fin = asuncion.localize(datetime.strptime('2021-08-12', "%Y-%m-%d"))
        fecha_fin_sprint_fin = asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d"))
        fecha_inicio_sprint_1 = asuncion.localize(datetime.strptime('2021-08-19', "%Y-%m-%d"))
        fecha_fin_sprint_1 = asuncion.localize(datetime.strptime('2021-08-25', "%Y-%m-%d"))
        fecha_inicio_sprint_2 = asuncion.localize(datetime.strptime('2021-08-26', "%Y-%m-%d"))
        fecha_fin_sprint_2 = asuncion.localize(datetime.strptime('2021-08-30', "%Y-%m-%d"))

        # Sprint Finalizado
        #
        # Creacion
        sprint_fin = Sprint.objects.create(
            fecha_inicio=fecha_inicio_sprint_fin,
            fecha_finalizacion=fecha_fin_sprint_fin,
            fecha_inicio_desarrollo=fecha_inicio_sprint_fin, fecha_finalizacion_real=fecha_fin_sprint_fin,
            proyecto=proyecto,
            proyecto_actual=proyecto,
            capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_fin, fecha_fin_sprint_fin)
        )
        for s_member in proyecto.scrum_member.all():
            CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                 saldo_horas=self.capacidad_dev[s_member.username],
                                                 sprint=sprint_fin, scrum_member=s_member)
            sprint_fin.scrum_member.add(s_member)
        sprint_fin.save()
        # Carga de Sprint Backlog
        us = proyecto.product_backlog.all().order_by('id')
        u_1 = us[1]
        u_2 = us[2]
        u_3 = us[3]
        u_1.sprint = sprint_fin
        u_1.save()
        u_2.sprint = sprint_fin
        u_2.save()
        u_3.sprint = sprint_fin
        u_3.save()
        #

        # Planificar User Stories
        de = proyecto.scrum_member.all().order_by('id')
        d_1 = de[1]
        d_2 = de[2]
        d_3 = de[3]
        u_1.desarrolladorAsignado = d_1
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se asigno al desarrolador " + d_1.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_2.desarrolladorAsignado = d_2
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se asigno al desarrolador " + d_1.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_3.desarrolladorAsignado = d_3
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se asigno al desarrolador " + d_1.username,
                                                fecha=fecha_inicio_sprint_fin)
        u_1.tiempoEstimadoSMaster = 20
        u_2.tiempoEstimadoSMaster = 20
        u_3.tiempoEstimadoSMaster = 20
        sprint_fin.horas_ocupadas_us += 60
        cap1 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_1)
        cap2 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_2)
        cap3 = CapacidadSMasteSprint.objects.get(sprint=sprint_fin, scrum_member=d_3)
        cap1.saldo_horas -= 20
        cap2.saldo_horas -= 20
        cap3.saldo_horas -= 20
        add_obj_perm_to_group('desarrollador_de_' + str(u_1.pk), 'desarrollar_user_story', u_1)
        add_user_to_obj_group(d_1, 'desarrollador_de_' + str(u_1.pk))
        add_obj_perm_to_group('desarrollador_de_' + str(u_2.pk), 'desarrollar_user_story', u_2)
        add_user_to_obj_group(d_2, 'desarrollador_de_' + str(u_2.pk))
        add_obj_perm_to_group('desarrollador_de_' + str(u_3.pk), 'desarrollar_user_story', u_3)
        add_user_to_obj_group(d_3, 'desarrollador_de_' + str(u_3.pk))
        d_1.save()
        d_2.save()
        d_3.save()
        u_1.save()
        u_2.save()
        u_3.save()
        cap1.save()
        cap2.save()
        cap3.save()
        sprint_fin.save()

        # Planning Poker
        sprint_fin.estado = 'conf2'
        sprint_fin.save()
        u_1.tiempoEstimado = 20
        u_2.tiempoEstimado = 20
        u_3.tiempoEstimado = 20
        u_1.save()
        u_2.save()
        u_3.save()

        # Inicio desarrollo
        sprint_fin.fecha_inicio_desarrollo = fecha_inicio_sprint_fin
        sprint_fin.duracion_estimada_dias = numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                               sprint_fin.fecha_finalizacion_real.date())
        sprint_fin.estado = 'conf3'
        u_1.estado = 'Doing'
        u_2.estado = 'Doing'
        u_3.estado = 'Doing'
        u_1.save()
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se paso a doing",
                                                fecha=fecha_inicio_sprint_fin)
        u_2.save()
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se paso a doing",
                                                fecha=fecha_inicio_sprint_fin)
        u_3.save()
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se paso a doing",
                                                fecha=fecha_inicio_sprint_fin)
        sprint_fin.save()

        # Registrar Actividades
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-12', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-15', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-16', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-17', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-12', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-15', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-16', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_1", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-12', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_2", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-16', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_3", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-17', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="descripcion_4", hora=5,
                                                fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        u_1.tiempoEnDesarrollo = 20
        u_2.tiempoEnDesarrollo = 20
        u_3.tiempoEnDesarrollo = 20
        u_1.save()
        u_2.save()
        u_3.save()

        # Marcar como done
        QA.objects.create(comentario="comentario", aceptar=True, user_story=u_1,
                          fecha=asuncion.localize(datetime.strptime('2021-08-17', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se acepto QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-08-17', "%Y-%m-%d")))
        QA.objects.create(comentario="comentario1", aceptar=True, user_story=u_2,
                          fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se acepto QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        QA.objects.create(comentario="comentario2", aceptar=True, user_story=u_3,
                          fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        RegistroActividadDiairia.objects.create(us=u_3, descripcion="Se acepto QA",
                                                fecha=asuncion.localize(datetime.strptime('2021-08-18', "%Y-%m-%d")))
        u_1.estado = 'Release'
        u_2.estado = 'Release'
        u_3.estado = 'Release'
        u_1.save()
        u_2.save()
        u_3.save()

        # Finalizar Sprint
        registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint_fin)
        horas_us_total = 0
        for us in sprint_fin.sprint_backlog.all():
            horas_us_total = horas_us_total + us.tiempoEstimado
        duracionSprint = sprint_fin.duracion_estimada_dias
        progreso = []
        progreso_act = []
        for x in range(0, duracionSprint + 1):
            progreso.append(horas_us_total)
            progreso_act.append(horas_us_total)
        for us in sprint_fin.sprint_backlog.all().order_by('id'):
            if hasattr(us, 'QA') and us.QA.aceptar:
                diferencia_dia = int(numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                        us.QA.fecha.date()))
                print(sprint_fin.fecha_inicio_desarrollo.date())
                print(us.QA.fecha.date())
                print(diferencia_dia)
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso[(duracionSprint) - i] -= us.tiempoEstimado
                    if progreso[(duracionSprint) - i] < 0:
                        progreso[(duracionSprint) - i] = 0

        for actividad in registros_de_actividad:
            if actividad.sprint == sprint_fin and actividad.hora > 0:
                diferencia_dia = int(numpy.busday_count(sprint_fin.fecha_inicio_desarrollo.date(),
                                                        actividad.fecha.date()))
                for i in range(0, duracionSprint + 1 - diferencia_dia):
                    progreso_act[(duracionSprint) - i] -= actividad.hora
        passed_days = duracionSprint
        sprint_fin.saved_us_progress = progreso
        sprint_fin.saved_act_progress = progreso_act
        sprint_fin.saved_horas_us_total = horas_us_total
        sprint_fin.fecha_finalizacion_real = sprint_fin.fecha_finalizacion
        sprint_fin.proyecto_actual = None
        sprint_fin.save()
        ##
        sprint_actual = sprint_fin
        sprint_sig = None
        ##
        if sprint_actual.estado == 'conf3':
            sprint_actual.estado = 'fin'
            for user_story in sprint_actual.sprint_backlog.all():
                if user_story.estado != 'Release':
                    user_story.estado = 'no-terminado'
                    user_story.desarrolladorAsignado = None
                    user_story.save()
            sprint_actual.proyecto_actual = None
            sprint_actual.fecha_finalizacion_real = sprint_fin.fecha_finalizacion
            sprint_actual.save()
            if hasattr(proyecto, "siguiente_sprint"):
                if proyecto.siguiente_sprint is not None:
                    sprint_sig.proyecto_actual = proyecto
                    sprint_sig.proyecto_sig = None
                    sprint_sig.save()
            proyecto.save()
            for us in sprint_fin.sprint_backlog.all():
                newUs = UserStorySprint.objects.create(descripcion=us.descripcion,
                                                       tiempoEstimadoSMaster=us.tiempoEstimadoSMaster,
                                                       tiempoEstimado=us.tiempoEstimado, estado=us.estado,
                                                       tiempoEnDesarrollo=us.tiempoEnDesarrollo, proyecto=us.proyecto,
                                                       sprintUs=us.sprint,
                                                       prioridad=us.prioridad, descripcionDone=us.descripcionDone,
                                                       desarrolladorAsignado=us.desarrolladorAsignado)
                for act in us.RegistroActividad.all():
                    RegistroActividadDiairia.objects.create(us2=newUs, descripcion=act.descripcion, fecha=act.fecha,
                                                            hora=act.hora)

            # Sprint Finalizado
            #
            # Creacion
            sprint_1 = Sprint.objects.create(
                fecha_inicio=fecha_inicio_sprint_1,
                fecha_finalizacion=fecha_fin_sprint_1,
                fecha_inicio_desarrollo=fecha_inicio_sprint_1, fecha_finalizacion_real=fecha_fin_sprint_1,
                proyecto=proyecto,
                proyecto_actual=proyecto,
                capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_1, fecha_fin_sprint_1)
            )
            for s_member in proyecto.scrum_member.all():
                CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                     saldo_horas=self.capacidad_dev[s_member.username],
                                                     sprint=sprint_1, scrum_member=s_member)
                sprint_1.scrum_member.add(s_member)
            sprint_1.save()
            # Carga de Sprint Backlog
            us = proyecto.product_backlog.all().order_by('id')
            u_1 = us[0]
            u_2 = us[4]
            u_1.sprint = sprint_1
            u_1.save()
            u_2.sprint = sprint_1
            u_2.save()
            #

            # Planificar User Stories
            de = proyecto.scrum_member.all().order_by('id')
            d_1 = de[0]
            d_2 = de[2]
            u_1.desarrolladorAsignado = d_1
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se asigno a " + d_1.username,
                                                    fecha=fecha_inicio_sprint_1)
            u_2.desarrolladorAsignado = d_2
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se asigno a " + d_2.username,
                                                    fecha=fecha_inicio_sprint_1)
            u_1.tiempoEstimadoSMaster = 20
            u_2.tiempoEstimadoSMaster = 20
            sprint_1.horas_ocupadas_us += 40
            cap1 = CapacidadSMasteSprint.objects.get(sprint=sprint_1, scrum_member=d_1)
            cap2 = CapacidadSMasteSprint.objects.get(sprint=sprint_1, scrum_member=d_2)
            cap1.saldo_horas -= 20
            cap2.saldo_horas -= 20
            add_obj_perm_to_group('desarrollador_de_' + str(u_1.pk), 'desarrollar_user_story', u_1)
            add_user_to_obj_group(d_1, 'desarrollador_de_' + str(u_1.pk))
            add_obj_perm_to_group('desarrollador_de_' + str(u_2.pk), 'desarrollar_user_story', u_2)
            add_user_to_obj_group(d_2, 'desarrollador_de_' + str(u_2.pk))
            d_1.save()
            d_2.save()
            u_1.save()
            u_2.save()
            cap1.save()
            cap2.save()
            sprint_1.save()

            # Planning Poker
            sprint_1.estado = 'conf2'
            sprint_1.save()
            u_1.tiempoEstimado = 20
            u_2.tiempoEstimado = 20
            u_1.save()
            u_2.save()

            # Inicio desarrollo
            sprint_1.fecha_inicio_desarrollo = fecha_inicio_sprint_1
            sprint_1.duracion_estimada_dias = numpy.busday_count(sprint_1.fecha_inicio_desarrollo.date(),
                                                                 sprint_1.fecha_finalizacion_real.date())
            sprint_1.estado = 'conf3'
            u_1.estado = 'Doing'
            u_2.estado = 'Doing'
            u_1.save()
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se paso a Doing",
                                                    fecha=fecha_inicio_sprint_1)
            u_2.save()
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se paso a Doing",
                                                    fecha=fecha_inicio_sprint_1)
            sprint_1.save()

            # Registrar Actividades
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_1", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-19', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_2", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-22', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_3", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-23', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_4", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-24', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_1", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-22', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_2", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-23', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_3", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-24', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="descripcion_4", hora=5,
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-25', "%Y-%m-%d")))

            u_1.tiempoEnDesarrollo = 20
            u_2.tiempoEnDesarrollo = 20
            u_1.save()
            u_2.save()

            # Marcar como done
            QA.objects.create(comentario="comentario", aceptar=True, user_story=u_1,
                              fecha=asuncion.localize(datetime.strptime('2021-08-24', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_1, descripcion="Se acepto QA",
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-24', "%Y-%m-%d")))
            QA.objects.create(comentario="comentario1", aceptar=True, user_story=u_2,
                              fecha=asuncion.localize(datetime.strptime('2021-08-25', "%Y-%m-%d")))
            RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se acepto QA",
                                                    fecha=asuncion.localize(
                                                        datetime.strptime('2021-08-25', "%Y-%m-%d")))
            u_1.estado = 'Release'
            u_2.estado = 'Release'
            u_1.save()
            u_2.save()

            # Finalizar Sprint
            registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint_1)
            horas_us_total = 0
            for us in sprint_1.sprint_backlog.all():
                horas_us_total = horas_us_total + us.tiempoEstimado
            duracionSprint = sprint_1.duracion_estimada_dias
            progreso = []
            progreso_act = []
            for x in range(0, duracionSprint + 1):
                progreso.append(horas_us_total)
                progreso_act.append(horas_us_total)
            for us in sprint_1.sprint_backlog.all().order_by('id'):
                if hasattr(us, 'QA') and us.QA.aceptar:
                    diferencia_dia = int(numpy.busday_count(sprint_1.fecha_inicio_desarrollo.date(),
                                                            us.QA.fecha.date()))
                    for i in range(0, duracionSprint + 1 - diferencia_dia):
                        progreso[(duracionSprint) - i] -= us.tiempoEstimado
                        if progreso[(duracionSprint) - i] < 0:
                            progreso[(duracionSprint) - i] = 0

            for actividad in registros_de_actividad:
                if actividad.sprint == sprint_1 and actividad.hora > 0:
                    diferencia_dia = int(numpy.busday_count(sprint_1.fecha_inicio_desarrollo.date(),
                                                            actividad.fecha.date()))
                    for i in range(0, duracionSprint + 1 - diferencia_dia):
                        progreso_act[(duracionSprint) - i] -= actividad.hora
            passed_days = duracionSprint
            sprint_1.saved_us_progress = progreso
            sprint_1.saved_act_progress = progreso_act
            sprint_1.saved_horas_us_total = horas_us_total
            sprint_1.fecha_finalizacion_real = sprint_1.fecha_finalizacion
            sprint_1.proyecto_actual = None
            sprint_1.save()
            ##
            sprint_actual = sprint_1
            sprint_sig = None
            ##
            if sprint_actual.estado == 'conf3':
                sprint_actual.estado = 'fin'
                for user_story in sprint_actual.sprint_backlog.all():
                    if user_story.estado != 'Release':
                        user_story.estado = 'no-terminado'
                        user_story.desarrolladorAsignado = None
                        user_story.save()
                sprint_actual.proyecto_actual = None
                sprint_actual.fecha_finalizacion_real = sprint_1.fecha_finalizacion
                sprint_actual.save()
                if hasattr(proyecto, "siguiente_sprint"):
                    if proyecto.siguiente_sprint is not None:
                        sprint_sig.proyecto_actual = proyecto
                        sprint_sig.proyecto_sig = None
                        sprint_sig.save()
                proyecto.save()
                for us in sprint_1.sprint_backlog.all():
                    newUs = UserStorySprint.objects.create(descripcion=us.descripcion,
                                                           tiempoEstimadoSMaster=us.tiempoEstimadoSMaster,
                                                           tiempoEstimado=us.tiempoEstimado, estado=us.estado,
                                                           tiempoEnDesarrollo=us.tiempoEnDesarrollo,
                                                           proyecto=us.proyecto,
                                                           sprintUs=us.sprint,
                                                           prioridad=us.prioridad, descripcionDone=us.descripcionDone,
                                                           desarrolladorAsignado=us.desarrolladorAsignado)
                    for act in us.RegistroActividad.all():
                        RegistroActividadDiairia.objects.create(us2=newUs, descripcion=act.descripcion, fecha=act.fecha,
                                                                hora=act.hora)
                # Sprint Finalizado
                #
                # Creacion
                sprint_2 = Sprint.objects.create(
                    fecha_inicio=fecha_inicio_sprint_2,
                    fecha_finalizacion=fecha_fin_sprint_2,
                    fecha_inicio_desarrollo=fecha_inicio_sprint_2, fecha_finalizacion_real=fecha_fin_sprint_2,
                    proyecto=proyecto,
                    proyecto_actual=proyecto,
                    capacidad_horas=self.calcularCapacidadDeSprint(proyecto, fecha_inicio_sprint_2, fecha_fin_sprint_2)
                )
                for s_member in proyecto.scrum_member.all():
                    CapacidadSMasteSprint.objects.create(capacidad_horas=self.capacidad_dev[s_member.username],
                                                         saldo_horas=self.capacidad_dev[s_member.username],
                                                         sprint=sprint_2, scrum_member=s_member)
                    sprint_2.scrum_member.add(s_member)
                sprint_2.save()
                # Carga de Sprint Backlog
                us = proyecto.product_backlog.all().order_by('id')
                u_1 = us[5]
                u_1.sprint = sprint_2
                u_1.save()
                #

                # Planificar User Stories
                de = proyecto.scrum_member.all().order_by('id')
                d_1 = de[0]
                u_1.desarrolladorAsignado = d_1
                RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se asigno a " + d_1.username,
                                                        fecha=fecha_inicio_sprint_2)
                u_1.tiempoEstimadoSMaster = 15
                sprint_2.horas_ocupadas_us += 15
                cap1 = CapacidadSMasteSprint.objects.get(sprint=sprint_2, scrum_member=d_1)
                cap1.saldo_horas -= 15
                add_obj_perm_to_group('desarrollador_de_' + str(u_1.pk), 'desarrollar_user_story', u_1)
                add_user_to_obj_group(d_1, 'desarrollador_de_' + str(u_1.pk))
                d_1.save()
                u_1.save()
                cap1.save()
                sprint_2.save()

                # Planning Poker
                sprint_2.estado = 'conf2'
                sprint_2.save()
                u_1.tiempoEstimado = 15
                u_1.save()

                # Inicio desarrollo
                sprint_2.fecha_inicio_desarrollo = fecha_inicio_sprint_2
                sprint_2.duracion_estimada_dias = numpy.busday_count(sprint_2.fecha_inicio_desarrollo.date(),
                                                                     sprint_2.fecha_finalizacion_real.date())
                sprint_2.estado = 'conf3'
                u_1.estado = 'Doing'
                RegistroActividadDiairia.objects.create(us=u_2, descripcion="Paso a doing",
                                                        fecha=fecha_inicio_sprint_2)
                u_1.save()
                sprint_2.save()

                # Registrar Actividades
                RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_1", hora=5,
                                                        fecha=asuncion.localize(
                                                            datetime.strptime('2021-08-26', "%Y-%m-%d")))
                RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_2", hora=5,
                                                        fecha=asuncion.localize(
                                                            datetime.strptime('2021-08-29', "%Y-%m-%d")))
                RegistroActividadDiairia.objects.create(us=u_1, descripcion="descripcion_4", hora=5,
                                                        fecha=asuncion.localize(
                                                            datetime.strptime('2021-08-30', "%Y-%m-%d")))

                u_1.tiempoEnDesarrollo = 15
                u_1.save()

                # Marcar como done
                QA.objects.create(comentario="comentario", aceptar=True, user_story=u_1,
                                  fecha=asuncion.localize(datetime.strptime('2021-08-30', "%Y-%m-%d")))
                RegistroActividadDiairia.objects.create(us=u_2, descripcion="Se acepto QA",
                                                        fecha=asuncion.localize(
                                                            datetime.strptime('2021-08-30', "%Y-%m-%d")))

                u_1.estado = 'Release'
                u_1.save()

                # Finalizar Sprint
                registros_de_actividad = RegistroActividadDiairia.objects.filter(us__sprint=sprint_2)
                horas_us_total = 0
                for us in sprint_2.sprint_backlog.all():
                    horas_us_total = horas_us_total + us.tiempoEstimado
                duracionSprint = sprint_2.duracion_estimada_dias
                progreso = []
                progreso_act = []
                for x in range(0, duracionSprint + 1):
                    progreso.append(horas_us_total)
                    progreso_act.append(horas_us_total)
                for us in sprint_2.sprint_backlog.all().order_by('id'):
                    if hasattr(us, 'QA') and us.QA.aceptar:
                        diferencia_dia = int(numpy.busday_count(sprint_2.fecha_inicio_desarrollo.date(),
                                                                us.QA.fecha.date()))
                        for i in range(0, duracionSprint + 1 - diferencia_dia):
                            progreso[(duracionSprint) - i] -= us.tiempoEstimado
                            if progreso[(duracionSprint) - i] < 0:
                                progreso[(duracionSprint) - i] = 0

                for actividad in registros_de_actividad:
                    if actividad.sprint == sprint_2 and actividad.hora > 0:
                        diferencia_dia = int(numpy.busday_count(sprint_2.fecha_inicio_desarrollo.date(),
                                                                actividad.fecha.date()))
                        for i in range(0, duracionSprint + 1 - diferencia_dia):
                            progreso_act[(duracionSprint) - i] -= actividad.hora
                passed_days = duracionSprint
                sprint_2.saved_us_progress = progreso
                sprint_2.saved_act_progress = progreso_act
                sprint_2.saved_horas_us_total = horas_us_total
                sprint_2.fecha_finalizacion_real = sprint_2.fecha_finalizacion
                sprint_2.proyecto_actual = None
                sprint_2.save()
                ##
                sprint_actual = sprint_2
                sprint_sig = None
                ##
                if sprint_actual.estado == 'conf3':
                    sprint_actual.estado = 'fin'
                    for user_story in sprint_actual.sprint_backlog.all():
                        if user_story.estado != 'Release':
                            user_story.estado = 'no-terminado'
                            user_story.desarrolladorAsignado = None
                            user_story.save()
                    sprint_actual.proyecto_actual = None
                    sprint_actual.fecha_finalizacion_real = sprint_2.fecha_finalizacion
                    sprint_actual.save()
                    if hasattr(proyecto, "siguiente_sprint"):
                        if proyecto.siguiente_sprint is not None:
                            sprint_sig.proyecto_actual = proyecto
                            sprint_sig.proyecto_sig = None
                            sprint_sig.save()
                    proyecto.save()
                    for us in sprint_2.sprint_backlog.all():
                        newUs = UserStorySprint.objects.create(descripcion=us.descripcion,
                                                               tiempoEstimadoSMaster=us.tiempoEstimadoSMaster,
                                                               tiempoEstimado=us.tiempoEstimado, estado=us.estado,
                                                               tiempoEnDesarrollo=us.tiempoEnDesarrollo,
                                                               proyecto=us.proyecto,
                                                               sprintUs=us.sprint,
                                                               prioridad=us.prioridad,
                                                               descripcionDone=us.descripcionDone,
                                                               desarrolladorAsignado=us.desarrolladorAsignado)
                        for act in us.RegistroActividad.all():
                            RegistroActividadDiairia.objects.create(us2=newUs, descripcion=act.descripcion,
                                                                    fecha=act.fecha,
                                                                    hora=act.hora)
        proyecto.estado = 'FIN'
        proyecto.fecha_fin = asuncion.localize(datetime.strptime('2021-09-01', "%Y-%m-%d"))
        for uw in proyecto.tiempos_de_usuarios.all():
            uw.delete()
        proyecto.save()

    def crearUSPorProyecto(self):
        print("...CREACION DE US POR PROYECTOS....\n\n")
        for x in userHistory:
            p = Proyecto.objects.get(slug=x['proyecto'])
            for y in x['us']:
                UserStory.objects.create(descripcion=y['descripcion'], descripcionDone=y['requisitos'], proyecto=p)
                SystemActivity.objects.create(usuario=self.admin,
                                              descripcion="Ha creado un user story en el proyecto " + x['proyecto'])

    def calcularCapacidadDeSprint(self, proyecto, fecha_incio, fecha_fin):
        # Calcular capacidad de sprint
        capacidad = 0
        self.capacidad_dev = {}
        for s_member in proyecto.scrum_member.all():
            self.capacidad_dev[s_member.username] = 0
        temp_date = fecha_incio
        dia = ''
        while temp_date <= fecha_fin:

            if temp_date.weekday() == 0:
                dia = 'LUN'
            elif temp_date.weekday() == 1:
                dia = 'MAR'
            elif temp_date.weekday() == 2:
                dia = 'MIE'
            elif temp_date.weekday() == 3:
                dia = 'JUE'
            elif temp_date.weekday() == 4:
                dia = 'VIE'
            else:
                dia = ''

            for work_user in proyecto.tiempos_de_usuarios.all():
                if work_user.dia == dia:
                    capacidad += work_user.horas
                    self.capacidad_dev[work_user.desarrollador.username] += work_user.horas
            temp_date = temp_date + timedelta(days=1)
        return capacidad
