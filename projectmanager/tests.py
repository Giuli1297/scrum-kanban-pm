from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.contrib.auth.models import User
# create your tests here.
from django.test import TestCase
from . import views
from django.urls.base import reverse,resolve



""" si el http status de la pagina es 200 es porque todo va bien
codigo 302  hace una redireccion temporal de una pagina a otra"""
class testmodeloautenticacion(TestCase):
    #setup para definir un escenario configurado para usar en los otros test
    def setUp(self):
        #crea un usuario
        user = User.objects.create(username='prueba')
        user.set_password('12345')
        user.save()
        self.register_home=reverse(views.homepage)
        return super().setUp()

    def test_login(self):
        #hacen login y si los datos son correctos retorna true
        logged_in = self.client.login(username='prueba', password='12345')
        self.assertTrue(logged_in)

    def test_login_false(self):
        #hace login pero con datos incorrectos
        #si los datos son incorrectos retorna true
        logged_in = self.client.login(username='prueb', password='12345')
        self.assertFalse(logged_in)
    def test_home(self):
        # ver pagina correctamente,deteccion de respuesta de modo que pudimos abrir la pagina correctamente
        response=self.client.get(self.register_home)
        self.assertEqual(response.status_code,200)#confirma si cargo correctamente la pagina
        self.assertTemplateUsed(response,'dashboard/home.html')#confirmacion de la plantilla usada
