from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name="home"),
    path('accounts/', include('allauth.urls')),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('proyectos/', views.ProyectoView.as_view(), name="proyecto_listar"),
    path('proyectos/crear/', views.ProyectoCreate.as_view(), name="proyecto_crear"),
    path('proyectos/<slug:slug>/editar/',views.ProyectoUpdate.as_view(),name="proyecto_editar"),
    path('proyectos/<slug:slug>/', views.ProyectoDetailView.as_view(), name='proyecto_detail'),
]
