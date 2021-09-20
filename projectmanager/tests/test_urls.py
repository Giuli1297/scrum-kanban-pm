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
        self.assertEquals(resolve(url).func.view_class, views.ProyectoView, 'Prueba 1')

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

    def test_ver_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para ver roles
        """
        url = reverse('list_rol')
        self.assertEquals(resolve(url).func.view_class, views.RolListView)

    def test_crear_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para crear roles
        """
        url = reverse('create_rol')
        self.assertEquals(resolve(url).func.view_class, views.RolCreateView)

    def test_actualizar_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para actualizar roles
        """
        url = reverse('update_rol', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.RolUpdateView)

    def test_eliminar_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para eliminar roles
        """
        url = reverse('delete_rol_rol', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.RolDeleteView)

    def test_ver_usuarios(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para ver los usuarios
        """
        url = reverse('list_user')
        self.assertEquals(resolve(url).func.view_class, views.ListUser)

    def test_asignar_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para asignar roles a usuarios
        """
        url = reverse('asignar_rol', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.AsignarRol)

    def test_eliminar_roles(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para eliminar roles de usuarios
        """
        url = reverse('delete_rol_user', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.EliminarRolUser) 
    
     def test_createUS(self):
            """
        Test para verificar que se carga correctamente la vista correspondiente para crear user story
        """
        url = reverse('create_us', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.UserStoryCreate) 
    
    def test_createSprint(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para crear un sprint
        """
        url = reverse('crear_sprint', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.CrearSprint) 
    
    def test_listar_sprint_backlog(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para lista sprint backlog
        """
        url = reverse('sprint_backlog', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.listaUsSprintBacklog) 
    
    def test_planning_poker_smaster(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente al smaster planning poker 
        """
        url = reverse('planning_poker_smaster', args=['slug'])
        self.assertEquals(resolve(url).func.view_class,  views.PlanningPokerView) 
    
    def test_planning_poker_estimar_sprint(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente planning poker, estimación de sprint 
        """
        url = reverse('estimar_sprint', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.EstimarSprint)
