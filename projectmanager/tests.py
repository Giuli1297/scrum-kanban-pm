from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.contrib.auth.models import User
# create your tests here.
from django.test import TestCase

from django.urls.base import reverse,resolve



""" si el http status de la pagina es 200 es porque todo va bien
codigo 302  hace una redireccion temporal de una pagina a otra"""
class testmodeloautenticacion(TestCase):
    #setup para definir un escenario configurado para usar en los otros test
    def setUp(self):
        user = User.objects.create(username='prueba')
        user.set_password('12345')
        user.save()
        return super().setUp()

    def test_login(self):
        logged_in = self.client.login(username='prueba', password='12345')
        self.assertTrue(logged_in)

    def test_login_false(self):
        logged_in = self.client.login(username='prueb', password='12345')
        self.assertFalse(logged_in)