from django.test import TestCase, Client

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from .. import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from ..models import Proyecto
from projectmanager.forms import ProyectoForm


class TestViews(TestCase):
    """
       Clase de Testing para vistas

    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.

        """
        self.client = Client()
        self.my_admin = User(username='user', is_staff=True, is_superuser=True)
        self.my_admin.set_password('passphrase')  # can't set above because of hashing
        self.my_admin.save()  # needed to save to temporary test db
        response = self.client.get('/admin/', follow=True)
        loginresponse = self.client.login(username='user', password='passphrase')
        self.proyecto = Proyecto.objects.create(nombre='slug', descripcion='xd', scrum_master=self.my_admin)
        self.assertTrue(loginresponse)

    def test_home_GET(self):
        """
        Testea que el template de home se cargue correctamenta

        """
        response = self.client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')

    def test_proyecto_list_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_listar'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_list.html')

    def test_proyecto_crear_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_crear'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_form.html')

    def test_proyecto_editar_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_editar', args=[self.proyecto.slug]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/proyecto_form.html')

    def test_proyecto_editarsm_GET(self):
        """
        Prueba que devuelva el template correcto
        """
        response = self.client.get(reverse('proyecto_editar_sm', args=[self.proyecto.slug]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'proyecto/detail.html')

    # def test_proyecto_crear_POST(self):
    #     form = ProyectoForm(data={
    #         'nombre': 'test 1',
    #         'descripcion': 'testtest test test',
    #         'scrum_master': self.my_admin
    #     })
    #     response = self.client.post(reverse('proyecto_crear'), follow=True)
    #
    #     # self.assertEquals(response.status_code, 302)
    #     self.assertEquals(Proyecto.objects.get(slug='proyecto-test').nombre, 'proyecto test')
