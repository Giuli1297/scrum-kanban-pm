from django.test import SimpleTestCase
from django.urls import reverse, resolve
from projectmanager import views


class TestUrlsUsuarios(SimpleTestCase):
    """
           Clase de Testing para Enlaces de Modulo de Usuarios
    """

    def test_home_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('home')
        self.assertEquals(resolve(url).func.view_class, views.HomePage)

    def test_activate_user_is_resolved(self):
        """
            Test que verifica que se carga correctamente las vista
        """
        url = reverse('activate', args=['token', 'uid'])
        self.assertEquals(resolve(url).func.view_class, views.VerificationView)

    def test_perfil_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('perfil')
        self.assertEquals(resolve(url).func, views.perfilUsuario)

    def test_system_activity_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('system_activity')
        self.assertEquals(resolve(url).func.view_class, views.SystemActivityView)


class TestUrlsRoles(SimpleTestCase):
    """
        Clase de Testing para Enlaces de Modulo de Roles de sistema
    """

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
        url = reverse('delete_rol', args=[1])
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

    def test_eliminar_rol_a_usuario(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para eliminar roles de usuarios
        """
        url = reverse('delete_rol_user', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.EliminarRolUser)


class TestUrlsProyecto(SimpleTestCase):
    """
        Clase de Testing para Enlaces de Modulo de Proyecto
    """

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

    def test_gestion_proyecto_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_gestion', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.GestionProyectoView)

    def test_editar_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_editar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoUpdate)

    def test_agregarsm_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_agregar_sm', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.AgregarSMember)

    def test_quitarsm_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_quitar_sm', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.QuitarSMember)

    def test_iniciar_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_iniciar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoIniciarView)

    def test_cancelar_proyecto_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('proyecto_cancelar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ProyectoCancelarView)


class TestUrlsProyectoRol(SimpleTestCase):
    """
        Clase de Testing para Enlaces de Modulo de Rol de Proyecto
    """

    def test_proyecto_rol_create_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para modificar rol de proyecto
        """
        url = reverse('proyecto_rol', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.CrearRolProyecto)

    def test_proyecto_rol_importar_url_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para modificar rol de proyecto
        """
        url = reverse('proyecto_rol_importar', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.ImportarRolProyecto)

    def test_proyecto_rol_modificar(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para modificar rol de proyecto
        """
        url = reverse('proyecto_rol_modificar', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.ModificarRolProyecto)

    def test_proyecto_rol_eliminar(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para eliminar rol de proyecto
        """
        url = reverse('proyecto_rol_eliminar', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.EliminarRolProyecto)


class TestUrlsUserStory(SimpleTestCase):
    """
        Clase de Testing para Enlaces de Modulo de User Stories
    """

    def test_createUS(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para crear user story
        """
        url = reverse('create_us', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.UserStoryCreate)

    def test_updateUS(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para acutalizar user story
        """
        url = reverse('update_us', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.UserStoryUpdate)

    def test_eliminarUS(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para eliminar user story
        """
        url = reverse('elimnar_us', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.EliminarUs)

    def test_historialUS(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para historial user story
        """
        url = reverse('historial_us', args=['slug', 1])
        self.assertEquals(resolve(url).func.view_class, views.listarLogHistorial)


class TestUrlsSprint(SimpleTestCase):
    """
        Clase de Testing para Enlaces de Modulo de Sprint
    """

    # path('planningPoker/<uidb64>/<token>/<int:usPk>/', views.PlanningPokerSMemberView.as_view(),
    #      name='planning_poker_smember'),

    def test_cargar_sprint_backlog_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('cargar_sprint_backlog', args=[1, 1])
        self.assertEquals(resolve(url).func.view_class, views.CargarSprintBacklog)

    def test_quitar_us_de_sbacklog_is_resolved(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('quitar_us_de_sbacklog', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.QuitarUSFromSprintBacklog)

    def test_asignar_estimar_user_story(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente para asignar y estimar sprint
        """
        url = reverse('asignar_estimar_user_story', args=[1])
        self.assertEquals(resolve(url).func.view_class, views.AsignarYEstimarUserStoryView)

    def test_planning_poker_smaster(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente al smaster planning poker 
        """
        url = reverse('planning_poker_smaster', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.PlanningPokerView)

    def test_planning_poker_smember(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente
        """
        url = reverse('planning_poker_smember', args=['slug', 'a', 1])
        self.assertEquals(resolve(url).func.view_class, views.PlanningPokerSMemberView)

    def test_planning_poker_estimar_sprint(self):
        """
        Test para verificar que se carga correctamente la vista correspondiente planning poker, estimación de sprint 
        """
        url = reverse('estimar_sprint', args=['slug'])
        self.assertEquals(resolve(url).func.view_class, views.EstimarSprint)
