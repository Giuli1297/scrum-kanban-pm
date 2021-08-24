from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('home', views.homepage2, name='home2'),
    path('accounts/', include('allauth.urls')),
    path('proyecto/<slug:proyecto_slug>/', views.proyecto_detail, name='proyecto_detail')
]
