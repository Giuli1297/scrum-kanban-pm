from django.test import SimpleTestCase, Client, TestCase
from projectmanager.forms import ProyectoForm, ProyectoUs
from projectmanager.models import Proyecto
from django.contrib.auth.models import User


class TestForms(TestCase):
    """
           Clase de Testing para formularios
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
        self.proyecto = Proyecto.objects.create(nombre='slug 1', descripcion='xd', scrum_master=self.my_admin)
        self.assertTrue(loginresponse)

    def test_proyecto_form_valid_data(self):
        """
        Test para verificor si los datos ingresados son correctos
        """
        form = ProyectoForm(data={
            'nombre': 'test 1',
            'descripcion': 'testtest test test',
            'scrum_master': self.my_admin
        })

        self.assertTrue(form.is_valid())

    def test_proyecto_form_no_valid_data(self):
        """
        Test para verificor si los datos ingresados son invalidos
        """
        form = ProyectoForm(data={
            'nombre': 'test 1',
            'descripcion': 'testtest test test'
        })

        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1) 
    
    def test_crear_user_story(self):
        """
        Test para verificar sin los datos ingresados son correctos en la cración de user story
        """
        form = ProyectoUs(data={
            'descripción_de_user_story': 'crear un servidor',
            'prioridad_1_al_10': 10
        })

        self.assertTrue(form.is_valid())
    

