from django.urls import path, include

from . import views

urlpatterns = [
    # URLS de Usuario
    path('', views.HomePage.as_view(), name="home"),
    path('accounts/', include('allauth.urls')),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('miperfil', views.perfilUsuario, name="perfil"),
    path('systemActivity', views.SystemActivityView.as_view(), name='system_activity'),

    # URLS DE ROLES
    path('roles/lista/', views.RolListView.as_view(), name='list_rol'),
    path('roles/create/', views.RolCreateView.as_view(), name='create_rol'),
    path('roles/update/<int:pk>/', views.RolUpdateView.as_view(), name='update_rol'),
    path('roles/delete/<int:pk>/', views.RolDeleteView.as_view(), name='delete_rol'),
    path('roles/users/', views.ListUser.as_view(), name='list_user'),
    path('roles/asignar/<int:pk>/', views.AsignarRol.as_view(), name='asignar_rol'),
    path('roles/deleteRolUser/<int:pk>/', views.EliminarRolUser.as_view(), name='delete_rol_user'),

    # URLS DE PROYECTO
    path('proyectos/listar/', views.ProyectoView.as_view(), name="proyecto_listar"),
    path('proyectos/crear/', views.ProyectoCreate.as_view(), name="proyecto_crear"),
    path('proyectos/<slug:slug>/gestionar/', views.GestionProyectoView.as_view(), name='proyecto_gestion'),
    path('proyectos/<slug:slug>/editar/', views.ProyectoUpdate.as_view(), name="proyecto_editar"),
    path('proyectos/<slug:slug>/editarsm/', views.AgregarSMember.as_view(), name="proyecto_agregar_sm"),
    path('proyectos/<slug:slug>/quitarsm/', views.QuitarSMember.as_view(), name="proyecto_quitar_sm"),
    path('proyectos/<slug:slug>/iniciar/', views.ProyectoIniciarView.as_view(), name="proyecto_iniciar"),
    path('proyectos/<slug:slug>/cancelar/', views.ProyectoCancelarView.as_view(), name="proyecto_cancelar"),
    path('proyectos/<slug:slug>/roles/', views.CrearRolProyecto.as_view(), name='proyecto_rol'),
    path('proyectos/<slug:slug>/roles/importar/', views.ImportarRolProyecto.as_view(),
         name='proyecto_rol_importar'),
    path('proyectos/<slug:slug>/roles/<int:pk>/', views.ModificarRolProyecto.as_view(), name='proyecto_rol_modificar'),
    path('proyectos/<slug:slug>/roles/<int:pk>/eliminar/', views.EliminarRolProyecto.as_view(),
         name='proyecto_rol_eliminar'),

    # URLS DE ROLES
    path('roles/lista/', views.RolListView.as_view(), name='list_rol'),
    path('roles/create/', views.RolCreateView.as_view(), name='create_rol'),
    path('roles/update/<int:pk>/', views.RolUpdateView.as_view(), name='update_rol'),
    path('roles/delete/<int:pk>/', views.RolDeleteView.as_view(), name='delete_rol'),
    path('roles/users/', views.ListUser.as_view(), name='list_user'),
    path('roles/asignar/<int:pk>/', views.AsignarRol.as_view(), name='asignar_rol'),
    path('roles/deleteRolUser/<int:pk>/', views.EliminarRolUser.as_view(), name='delete_rol_user'),
    path('proyectos/<slug:slug>/createUs/', views.UserStoryCreate.as_view(), name='create_us'),
    path('proyectos/<slug:slug>/updateUs/<int:pk>/', views.UserStoryUpdate.as_view(), name='update_us'),
    path('proyectos/<slug:slug>/eliminarUs/<int:pk>/', views.EliminarUs.as_view(), name='elimnar_us'),
    path('proyectos/<slug:slug>/crearSprint/', views.CrearSprint.as_view(), name='crear_sprint'),
    path('proyectos/<slug:slug>/actualizarSprint/<int:pk>/', views.ActualizarSprint.as_view(),
         name='actualizar_sprint'),
    path('proyectos/<slug:slug>/listarSprintBacklog/<int:pk>/', views.listaUsSprintBacklog.as_view(),
         name='sprint_backlog'),
    path('proyectos/<slug:slug>/configurarUS/<int:pk>/', views.UserStoryUpdateSprint.as_view(), name='configurar_us'),

    # URLS DE USER STORY
    path('proyectos/<slug:slug>/createUs/', views.UserStoryCreate.as_view(), name='create_us'),
    path('proyectos/<slug:slug>/updateUs/<int:pk>/', views.UserStoryUpdate.as_view(), name='update_us'),
    path('proyectos/<slug:slug>/eliminarUs/<int:pk>/', views.EliminarUs.as_view(), name='elimnar_us'),
    path('proyectos/<slug:slug>/historial/<int:pk>/', views.listarHistorial.as_view(), name='historial_us'),

    # URLS DE SPRINTS
    path('proyectos/<slug:slug>/listarSprintBacklog/<int:pk>/', views.listaUsSprintBacklog.as_view(),
         name='sprint_backlog'),
    path('proyectos/<slug:slug>/configurarUS/<int:pk>/', views.UserStoryUpdateSprint.as_view(), name='configurar_us'),
    path('proyectos/cargarSprintBacklog/<int:usPk>/<int:sprintPk>/', views.CargarSprintBacklog.as_view(),
         name='cargar_sprint_backlog'),
    path('proyectos/quitarUSFromSprintBacklog/<int:usPk>/', views.QuitarUSFromSprintBacklog.as_view(),
         name='quitar_us_de_sbacklog'),
    path('proyectos/asignarYEstimarUS/<int:usPk>/', views.AsignarYEstimarUserStoryView.as_view(),
         name='asignar_estimar_user_story'),
    path('planningPoker/<slug:slug>/', views.PlanningPokerView.as_view(), name='planning_poker_smaster'),
    path('planningPoker/<uidb64>/<token>/<int:usPk>/', views.PlanningPokerSMemberView.as_view(),
         name='planning_poker_smember'),
    path('planningPoker/<slug:slug>/estimarSprint/', views.EstimarSprint.as_view(), name='estimar_sprint')

]
