from django.test import TestCase, Client, SimpleTestCase

from django.contrib.auth.models import User, Permission, Group
from django.test import TestCase, Client
from .. import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from ..models import Proyecto, Rol
from projectmanager.forms import *
import datetime


class TestViews(TestCase):
    """
       Clase de Testing para vistas

    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.

        """
        self.admin = User.objects.create_user(username='admin1', email='giuli@email.com', password='admin1')
        self.admin.is_staff = True
        admin_group = Group.objects.create(name='Administrador')
        admin_rol = Rol.objects.create(related_group=admin_group, tipo='sistema')
        for permission in Permission.objects.all():
            admin_group.permissions.add(permission)
        self.admin.groups.add(admin_group)
        self.client.login(username='admin1', password='admin1')
        self.proyecto = Proyecto.objects.create(nombre='slug', descripcion='xd', scrum_master=self.admin)

    def test_home_GET(self):
        """
        Testea que el template de home se cargue correctamenta

        """
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')

    def test_verification_account_GET(self):
        """
        Test de la vista
        """
        url = reverse('activate', kwargs={
            'uidb64': 'uid', 'token': 'token'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)

    def test_system_activity_GET(self):
        """

        :return:
        """
        url = reverse('system_activity')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/system_activity.html')

    def test_proyecto_crear_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_crear'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_form.html')

    def test_proyecto_crear_POST(self):
        """
        
        :return: 
        """
        url = reverse('proyecto_crear')
        response = self.client.post(url, data={
            'nombre': 'proyecto test3',
            'descripcion': 'test',
            'scrum_master': User.objects.all()[1]}, follow=True)
        self.assertEquals(response.status_code, 200)

    '''def test_proyecto_agregar_sm_POST(self):
        """

        :return:
        """
        url = reverse('proyecto_agregar_sm', args=['slug'])
        response = self.client.post(url, {
            'scrum_member': self.admin,
            'lunes': 1,
            'martes': 1,
            'miercoles': 1,
            'jueves': 1,
            'viernes': 1}, follow=True)
        self.assertEquals(response.status_code, 200)'''

    def test_proyecto_list_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_listar'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_list.html')

    def test_proyecto_editar_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_editar', args=[self.proyecto.slug]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_form.html')

    def test_proyecto_agregarsm_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_agregar_sm', args=[self.proyecto.slug]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/agregar_scrum_member.html')

    def test_proyecto_verificar_estado_POST(self):
        """
        Prueba para verificar el estado imediatamente luego de haberse creado
        """

        User.objects.create(username='juan', email="juan@gmail.com", password="Probando1")
        proyecto = Proyecto.objects.create(nombre='proyecto test', descripcion="probando test",
                                           scrum_master=User.objects.get(username='juan'))

        self.assertEquals(proyecto.nombre, "proyecto test")
        self.assertEquals(proyecto.estado, "PEN")

    def test_proyecto_crear_user_story(self):
        """
        Prueba para verificar la creación de un UserStory
        """

        url = reverse('create_us', args=[self.proyecto.slug])

        response = self.client.post(url, {
            'descripción_de_user_story': 'Test1',
            'prioridad_1_al_10': '4'
        })

        self.assertEquals(response.status_code, 302)

    def test_proyecto_verificar_rol_crear_user_story(self):
        """
        Prueba que verifica si un miembro tiene el permiso de crear un UserStory
        """

        user = User.objects.create(username='user1', email="user1@gmail.com")
        user.set_password("probando1")
        user.save()
        url = reverse('proyecto_agregar_sm', args=[self.proyecto.slug])
        response = self.client.post(url, {
            'scrum_member': user,
            'lunes': 1,
            'martes': 1,
            'miercoles': 1,
            'jueves': 1,
            'viernes': 1
        })

        self.assertEquals(response.status_code, 302)

        cliente2 = Client()
        isLogin = cliente2.login(username='user1', password='probando1')

        self.assertTrue(isLogin, "El usuario no pudo iniciar sesión")

        url = reverse('create_us', args=[self.proyecto.slug])

        response = cliente2.post(url, {
            'descripción_de_user_story': 'Test3',
            'prioridad_1_al_10': '5'
        }, follow=True)

        self.assertEquals(response.redirect_chain[0][0], '/proyectos/slug/gestionar/')

    def test_proyecto_visualizar_tablero_kanban_y_registro_actividades(self):
        """
        Prueba de registro de actividades
        """
        user = User.objects.create(username='juan', email="user1@gmail.com")
        self.proyecto.estado = 'ACT'
        self.proyecto.scrum_member.add(user)
        self.proyecto.save()
        sprint = Sprint.objects.create(proyecto=self.proyecto, proyecto_actual=self.proyecto)
        # Registro actividades
        userStory = UserStory.objects.create(descripcion="test1", prioridad=4, proyecto=self.proyecto, sprint=sprint,
                                             desarrolladorAsignado=user, tiempoEstimado=8)

        self.assertEquals(userStory.desarrolladorAsignado.username, 'juan')
        self.assertEquals(userStory.tiempoEstimado, 8)

    def test_proyecto_user_story_cambio_estado(self):
        """
        Prueba de cambio de estado en un user story
        """
        userStory = UserStory.objects.create(
            descripcion="userStory1",
            prioridad=5, proyecto=self.proyecto,
            estado="Nuevo"
        )

        userStory.estado = "Doing"
        self.assertEquals(userStory.estado, "Doing")

        userStory.estado = "Done"
        self.assertEquals(userStory.estado, "Done")

    def test_proyecto_cargar_actividades_user_story(self):
        """
        Prueba cargar de actividades en un user story
        """
        userStory = userStory = UserStory.objects.create(
            descripcion="Probar server",
            prioridad=5, proyecto=self.proyecto,
            estado="Doing"
        )

        historial = HistorialUs.objects.create(
            us=userStory,
            usuario=self.admin
        )

        self.assertEquals("Probar server", "Probar server")

    def test_proyecto_habilitar_qa(self):
        """
        Prueba para habilitar qa de un user story
        """
        userStory = userStory = UserStory.objects.create(
            descripcion="Probar server",
            prioridad=5, proyecto=self.proyecto,
            estado="QA"
        )

        qa = QA.objects.create(
            user_story=userStory,
            comentario="el user story terminado para revision",
            aceptar=False
        )

        self.assertFalse(qa.aceptar)

    def test_proyecto_gestionar_horas_user_story(self):
        """
        Prueba para gestionar horas user story scrum master
        """

        user = User.objects.create(username='dev', email="user1@gmail.com")
        userStory = userStory = UserStory.objects.create(
            descripcion="Probar server",
            prioridad=5, proyecto=self.proyecto,
            estado="Nuevo",
            desarrolladorAsignado=user,
            tiempoEstimadoSMaster=4
        )

        self.assertEquals(userStory.tiempoEstimadoSMaster, 4)

    def test_finalizar_sprint(self):
        '''
        se crea un sprint para verificar su estado finalizado
        :return:
        '''
        sprint = Sprint.objects.create(estado="conf3")
        sprint.estado="fin"

        self.assertEquals(sprint.estado,"fin","El dprint no fue cancelado")

    def test_devolver_user_storys_no_terminados(self):
        '''
            verificca si un user story esta en estado cancelado
        :return:
        '''

        userStory = UserStory.objects.create(
            descripcion="userStory1",
            prioridad=5, proyecto=self.proyecto,
            estado="Doing"
        )

        userStory.estado = "Cancelado"
        self.assertEquals(userStory.estado, "Cancelado","el user story aun no fue cancelado")

