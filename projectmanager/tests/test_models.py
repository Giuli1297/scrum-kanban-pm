from django.test import TestCase

from django.contrib.auth.models import User
from django.test import TestCase, Client
from .. import views
from django.urls.base import reverse, resolve
# Create your tests here.
from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from ..models import Proyecto


class TestModeloProyecto(TestCase):
    def setUp(self):
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
        url = reverse('proyecto_editar_sm', args=[self.data1.slug])
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
        '''

        testea el registro de un email valido

        '''

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
        self.assertEquals(self.proyecto.slug, 'slug-1')
