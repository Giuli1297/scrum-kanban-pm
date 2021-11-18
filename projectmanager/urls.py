from django.urls import path, include

from . import views

urlpatterns = [
    # URLS de Usuario
    path('', views.HomePage.as_view(), name="home"),
    path('accounts/', include('allauth.urls')),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('miperfil/', views.perfilUsuario, name="perfil"),
    path('systemActivity/', views.SystemActivityView.as_view(), name='system_activity'),

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
    path('proyectos/<slug:slug>/reporte/', views.VistaReporteView.as_view(), name='proyecto_reporte'),
    path('proyectos/<slug:slug>/vista-pdf-product_backlog/', views.ViewPdfProductBacklog.as_view(), name='proyecto_pdf_product_backlog'),
    path('proyectos/<slug:slug>/<int:pk>/vista-pdf-sprint_backlog/', views.ViewPdfSpringBacklog.as_view(), name='proyecto_pdf_product_backlog'),
    path('proyectos/<slug:slug>/vista-pdf-us-prioridad/', views.ViewPdfUSPrioridad.as_view(), name='proyecto_pdf_us_prioridad'),
    path('proyectos/<slug:slug>/editar/', views.ProyectoUpdate.as_view(), name="proyecto_editar"),
    path('proyectos/<slug:slug>/editarsm/', views.AgregarSMember.as_view(), name="proyecto_agregar_sm"),
    path('proyectos/<slug:slug>/quitarsm/', views.QuitarSMember.as_view(), name="proyecto_quitar_sm"),
    path('proyectos/<slug:slug>/iniciar/', views.ProyectoIniciarView.as_view(), name="proyecto_iniciar"),
    path('proyectos/<slug:slug>/cancelar/', views.ProyectoCancelarView.as_view(), name="proyecto_cancelar"),

    # URLS DE ROLES DE PROYECTO
    path('proyectos/<slug:slug>/roles/', views.CrearRolProyecto.as_view(), name='proyecto_rol'),
    path('proyectos/<slug:slug>/roles/importar/', views.ImportarRolProyecto.as_view(),
         name='proyecto_rol_importar'),
    path('proyectos/<slug:slug>/roles/<int:pk>/', views.ModificarRolProyecto.as_view(), name='proyecto_rol_modificar'),
    path('proyectos/<slug:slug>/roles/<int:pk>/eliminar/', views.EliminarRolProyecto.as_view(),
         name='proyecto_rol_eliminar'),
    path('proyecto/list-users-by-group', views.get_list_users_group, name='poryecto_rol_usuarios'),
    path('proyecto/cambiar_dev', views.cambiar_dev_en_US, name='poryecto_cambiar_usuario_US_sprint'),
    path('proyecto/list-users-by-sprint_current', views.get_list_user_current_sprint, name='poryecto_users_sprint'),
    path('proyectos/<slug:slug>/finalizarProyecto/', views.FinalizarProyecto.as_view(), name='finalizar_proyecto'),

    # URLS DE USER STORY
    path('proyectos/<slug:slug>/createUs/', views.UserStoryCreate.as_view(), name='create_us'),
    path('proyectos/<slug:slug>/updateUs/<int:pk>/', views.UserStoryUpdate.as_view(), name='update_us'),
    path('proyectos/<slug:slug>/eliminarUs/<int:pk>/', views.EliminarUs.as_view(), name='elimnar_us'),
    path('proyectos/<slug:slug>/historial/<int:pk>/', views.listarHistorial.as_view(), name='historial_us'),
    path('proyectos/<slug:slug>/revertir/<int:pk>/', views.RevertirHistorial.as_view(), name='revertir_us'),
    # path('proyectos/<slug:slug>/historial/<int:pk>/', views.listarLogHistorial.as_view(), name='historial_us'),

    # URLS DE SPRINTS
    path('proyectos/<slug:slug>/planificar_sprint/', views.PlanificarSprint.as_view(), name='crear_sprint'),
    path('proyectos/cargarSprintBacklog/<int:usPk>/<int:sprintPk>/', views.CargarSprintBacklog.as_view(),
         name='cargar_sprint_backlog'),
    path('proyectos/quitarUSFromSprintBacklog/<int:usPk>/', views.QuitarUSFromSprintBacklog.as_view(),
         name='quitar_us_de_sbacklog'),
    path('proyectos/asignarYEstimarUS/<int:usPk>/', views.AsignarYEstimarUserStoryView.as_view(),
         name='asignar_estimar_user_story'),
    path('planningPoker/<uidb64>/<token>/<int:usPk>/', views.PlanningPokerSMemberView.as_view(),
         name='planning_poker_smember'),
    path('planningPoker/<slug:slug>/<int:sprintPk>/', views.PlanningPokerView.as_view(), name='planning_poker_smaster'),
    path('planningPoker/<slug:slug>/estimarSprint/', views.EstimarSprint.as_view(), name='estimar_sprint'),
    path('proyectos/confirmFinalizarSprint/<int:sprintPk>/', views.ConfirmarFinalizarSprint.as_view(),
         name='confirmar_finalizar_sprint'),
    path('proyectos/finalizarSprint/<int:sprintPk>/', views.FinalizarSprint.as_view(), name='finalizar_sprint'),
    path('proyectos/sprint/<int:sprintPk>/', views.VerSprintDetail.as_view(), name='ver_sprint_detail'),
    path('proyectos/extenderSprint/<slug:slug>/', views.ExtenderSprint.as_view(), name='extender_sprint'),

    # URLS DE KANBAN
    path('kanban/<int:usPk>/seleccionarpararealizar/', views.SeleccionarParaRealizarUserStory.as_view(),
         name='seleccionar_p_realizar_user_story'),
    path('proyectos/<slug:slug>/burndownchart/<int:sprintPk>/', views.VerBurndownChartView.as_view(),
         name='ver_burndownchart_actual'),
    path('proyectos/<slug:slug>/dataBurndownChart/<int:sprintPk>/', views.getDataForBurndownChart.as_view(),
         name='data_burndownchart'),
    path('proyectos/<slug:slug>/RegistroActividad/<int:pk>/', views.RegistroDiario.as_view(),
         name='registro_actividad'),
    path('proyectos/<slug:slug>/RegistroActividadUpdate/<int:pk>/<int:uspk>/', views.RegistroDiarioUpdate.as_view(),
         name='registro_actividad_update'),
    path('proyectos/<slug:slug>/RegistroActividadDelete/<int:pk>/<int:uspk>/', views.RegistroDiarioDelete.as_view(),
         name='registro_actividad_delete'),
    path('proyectos/<slug:slug>/marcarUSDone/<int:usPk>/', views.MarcarUSComoDoneView.as_view(), name='marcar_us_done'),
    path('proyectos/<slug:slug>/realizarQA/<int:usPk>/', views.RealizarQAUSView.as_view(), name='realizar_qa'),

]
