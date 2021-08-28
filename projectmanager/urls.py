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
]
