# import pytest as pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.test import TestCase, Client
from .. import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from ..models import Proyecto

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from projectmanager import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm

from projectmanager.models import Proyecto

from projectmanager.models import Proyecto, Rol

from projectmanager.views import *


class TestModeloProyecto(TestCase):
    """
    Clase de Testing para formularios
    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.
        """
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        user = User.objects.create_user(**self.credentials)
        nombre = 'test'
        slug = 'test'
        descripcion = 'testtest'
        estado = 'PEN'
        scrum_master = User.objects.create(username='test', password='test')
        self.data1 = Proyecto.objects.create(nombre=nombre, slug=slug, descripcion=descripcion, estado=estado,
                                             scrum_master=scrum_master)
        self.data2 = Proyecto.objects.create(nombre=nombre + '2', slug=slug + '2', descripcion=descripcion,
                                             estado=estado,
                                             scrum_master=scrum_master)

    def test_proyecto_model_entry(self):
        """
        Test product model data insertion/types/field attributes
        """
        data = self.data1
        self.assertTrue(isinstance(data, Proyecto))
        self.assertEqual(str(data), 'test')

    def test_proyecto_url(self):
        """
        Test product model slug and URL reverse
        """
        loin = self.client.login(username='testuser', password='secret')
        url = reverse('proyecto_agregar_sm', args=[self.data1.slug])
        self.assertEqual(url, '/proyectos/test/editarsm/')


class TestModeloAutenticacion(TestCase):
    """
    Clase de Testing para funciones como log-in, log-aut, sign-up

    ...

    Methods
    -------
    setUp()

    test_login()

    test_login_false()

    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.

        """
        user = User.objects.create(username='prueba')
        user.set_password('12345')
        user.save()
        self.register_home = reverse('home')
        return super().setUp()

    def test_login(self):
        """
        Testea el log-in de un usuario existente

        """
        logged_in = self.client.login(username='prueba', password='12345')
        self.assertTrue(logged_in)

    def test_login_false(self):
        """
        Testea el log-in de un usuario con credenciales incorrectas

        """
        logged_in = self.client.login(username='prueb', password='12345')
        self.assertFalse(logged_in)

    def test_signup_email_verification(self):
        """

        testea el registro de un email valido

        """

        data = {
            "username": "user",
            "email": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertTrue(form.is_valid())


class TestModels(TestCase):
    def setUp(self):
        self.client = Client()
        self.my_admin = User(username='user', is_staff=True, is_superuser=True)
        self.my_admin.set_password('passphrase')  # can't set above because of hashing
        self.my_admin.save()  # needed to save to temporary test db
        response = self.client.get('/admin/', follow=True)
        loginresponse = self.client.login(username='user', password='passphrase')
        self.proyecto = Proyecto.objects.create(nombre='slug 1', descripcion='xd', scrum_master=self.my_admin)
        self.assertTrue(loginresponse)

    def test_proyecto_is_assigned_slug_on_creation(self):
        """
        Testea que una vez creado el proyeto el slug sea correcto
        """
        self.assertEquals(self.proyecto.slug, 'slug-1')


class TestModelss(TestCase):
    """
    crea un grupo que seria igual a un rol
    crea un usuario par asignarle un rol
    """

    def setUp(self):
        nombre_rol = "grupo1"
        self.roles = Group.objects.create(name=nombre_rol)
        self.roles.save()
        self.c = Client()
        self.user = User.objects.create_user(username="test", email="test@test.com", password="test")

    def test_create_rol(self):
        """
        retorna true si el nombre del rol creado es igual al otro argumento ,
        """
        self.assertEqual(self.roles.name, "grupo1")

    def test_asignar_rol(self):
        """
        asigna un role o grupo a un usuario
        """
        self.user.groups.add(self.roles)
        self.assertTrue(self.user.groups.filter(name="grupo1"))

    def test_elimiar_rol_de_usuario(self):
        """
        elimina el rol o grupo de usuario
        restorna true si es que eliminó correctamente el rol del usuario
        """
        self.user.groups.remove(self.roles)
        self.assertFalse(self.user.groups.filter(name="grupo1"))

    def test_eliminar_rol(self):
        """
        se elimina el rol
        etorna true si es que se elimió correctamente el rol
        """
        self.roles = self.roles.delete()
        self.assertFalse(self.user.groups.filter(name="grupo1"))


class TestModelUs(TestCase):
    '''
    clase para verificar las asignaciones de proyectos, usuarios, sprint a un user story

    '''
    def setUp(self):
        descripcion_us="us"
        self.userStorys=UserStory.objects.create(descripcion=descripcion_us)
        self.userStorys.save()
        self.user = User.objects.create(username='prueba')
        self.user.set_password('12345')
        self.user.save()
        self.proyecto=Proyecto.objects.create(nombre='proyecto1',scrum_master=self.user)
        self.proyecto.save()
        self.sprint=Sprint.objects.create(proyecto=self.proyecto,proyecto_actual=self.proyecto)
        self.sprint.save()

    def test_create_us(self):
        '''
            verifica s se creó correctamente un user story
        '''
        self.assertEqual(self.userStorys.descripcion, "us")

    def test_asignar_us(self):
        '''
            se crea y se asigna un usuario a un user story
        :return:
        '''
        self.userStorys.desarrolladorAsignado=self.user
        self.assertEqual(self.userStorys.desarrolladorAsignado.username,'prueba',"verifica si se asignó correctamente un usuario a un user story")
    def test_asignar_proyecto_a_us(self):
        '''
        se crea y se asigna un proyecto a un user story
        :return:
        '''
        self.userStorys.proyecto=self.proyecto
        self.assertEqual(self.userStorys.proyecto.nombre,"proyecto1","verifica si se asignó correctamente un proyecto a un user story")
    def test_asignar_sprint_a_us(self):
        '''
        se crea y se asigna un sprint a un user story
        :return:
        '''
        self.userStorys.sprint=self.sprint
        self.assertEqual(self.userStorys.sprint.proyecto.nombre,"proyecto1","verifica si se asignó correctamente un sprint a un user story")

    def test_historial_us(self):
        '''
        se crea un historial y se le asigna un user story
        :return:
        '''
        self.historial=HistorialUs.objects.create(us=self.userStorys)
        self.assertEquals(self.historial.us,self.userStorys,"verifica si se asigna bien un user story a un objeto historial de user story  ")




