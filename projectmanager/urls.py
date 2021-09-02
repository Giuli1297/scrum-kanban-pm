from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('accounts/', include('allauth.urls')),
    path('proyecto/<slug:proyecto_slug>/', views.proyecto_detail, name='proyecto_detail'),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('proyectos/crear/', views.ProyectoCreate.as_view(), name="proyecto_crear"),
    path('proyectos/listar/',views.ProyectoView.as_view(), name="proyecto_listar"),
    path('proyectos/editar/<slug:slug>/',views.ProyectoUpdate.as_view(),name="proyecto_editar"),
    path('roles/lista/',views.RolListView.as_view(),name='list_rol'),
    path('roles/create/',views.RolCreateView.as_view(),name='create_rol'),
    path('roles/update/<int:pk>/',views.RolUpdateView.as_view(),name='update_rol'),
    path('roles/delete/<int:pk>/',views.RolDeleteView.as_view(),name='delete_rol'),
    path('roles/users/',views.ListUser.as_view(),name='list_user'),
    path('roles/asignar/<int:pk>/',views.AsignarRol.as_view(),name='asignar_rol'),

]
