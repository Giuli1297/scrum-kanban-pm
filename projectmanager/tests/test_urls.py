from django.test import SimpleTestCase
from django.urls import reverse, resolve
from projectmanager import views


class TestUrls(SimpleTestCase):
    """
           Clase de Testing para Enlaces
    """
    def test_home_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('home')
        self.assertEquals(resolve(url).func.view_class, views.HomePage)

    def test_list_proyectos_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_listar')
        self.assertEquals(resolve(url).func.view_class, views.ProyectoView)

    def test_crear_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_crear')
        self.assertEquals(resolve(url).func.view_class, views.ProyectoCreate)


    def test_editar_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_editar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoUpdate)


    def test_editarsm_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_editar_sm', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoSMUpdate)


    def test_iniciar_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_iniciar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoIniciarView)
