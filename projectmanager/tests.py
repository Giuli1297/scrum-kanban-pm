from django.test import TestCase

from django.contrib.auth.models import User
from django.test import TestCase
from . import views
from django.urls.base import reverse,resolve
# Create your tests here.


class TestModeloAutenticacion(TestCase):
    """
    Clase de Testing para funciones como log-in, log-aut, sign-up

    ...

    Methods
    -------
    setUp()
        Deja listo variables que se utilizaran para los test
    test_login()
        Prueba la funcionalidad de logearse de un usuario existente
    test_login_false()
        Prueba que un usuario con credenciales incorrectas no se pueda logear
    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.

        """
        user = User.objects.create(username='prueba')
        user.set_password('12345')
        user.save()
        self.register_home=reverse(views.homepage)
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

class TestHomePage(TestCase):
    """
    Clase de Testing para funciones de la pagina principal

    ...

    Methods
    -------
    setUp()
        Deja listo variables que se utilizaran para los test
    test_home()
        Prueba que se cargue el template correcto
    """

    def setUp(self):
        """
        Deja listas las variables para que se utilicen en los tests.

        """
        self.register_home=reverse(views.homepage)
        return super().setUp()

    def test_home(self):
        """
        Testea que el template de home se cargue correctamenta

        """
        response=self.client.get(self.register_home)
        self.assertEqual(response.status_code,200)#confirma si cargo correctamente la pagina
        self.assertTemplateUsed(response,'dashboard/home.html')#confirmacion de la plantilla usada
