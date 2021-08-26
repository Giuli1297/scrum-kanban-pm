from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('accounts/', include('allauth.urls')),
    path('proyecto/<slug:proyecto_slug>/', views.proyecto_detail, name='proyecto_detail'),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
]
