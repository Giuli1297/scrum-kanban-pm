from django.test import TestCase, Client, SimpleTestCase

from django.contrib.auth.models import User, Permission, Group
from django.test import TestCase
from .. import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from ..models import Proyecto, Rol
from projectmanager.forms import *


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

    def test_proyecto_agregar_sm_POST(self):
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
        self.assertEquals(response.status_code, 200)

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
