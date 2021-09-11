from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name="home"),
    path('accounts/', include('allauth.urls')),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('proyectos/', views.ProyectoView.as_view(), name="proyecto_listar"),
    path('proyectos/crear/', views.ProyectoCreate.as_view(), name="proyecto_crear"),
    path('proyectos/<slug:slug>/editar/', views.ProyectoUpdate.as_view(), name="proyecto_editar"),
    path('proyectos/<slug:slug>/editarsm/', views.ProyectoSMUpdate.as_view(), name="proyecto_editar_sm"),
    path('proyectos/<slug:slug>/iniciar/', views.ProyectoIniciarView.as_view(), name="proyecto_iniciar"),
    path('miperfil', views.perfilUsuario, name="perfil"),
    path('proyectos/listar/', views.ProyectoView.as_view(), name="proyecto_listar"),
    path('proyectos/editar/<slug:slug>/', views.ProyectoUpdate.as_view(), name="proyecto_editar"),
    path('roles/lista/', views.RolListView.as_view(), name='list_rol'),
    path('roles/create/', views.RolCreateView.as_view(), name='create_rol'),
    path('roles/update/<int:pk>/', views.RolUpdateView.as_view(), name='update_rol'),
    path('roles/delete/<int:pk>/', views.RolDeleteView.as_view(), name='delete_rol'),
    path('roles/users/', views.ListUser.as_view(), name='list_user'),
    path('roles/asignar/<int:pk>/', views.AsignarRol.as_view(), name='asignar_rol'),
    path('roles/deleteRolUser/<int:pk>/', views.EliminarRolUser.as_view(), name='delete_rol_user'),
    path('proyecto/createUs/ ',views.UserStoryCreate.as_view(),name='create_us'),
    path('us/updateUs/<int:pk>/',views.UserStoryUpdate.as_view(),name='update_us'),

]
