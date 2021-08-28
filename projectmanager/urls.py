from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('accounts/', include('allauth.urls')),
    path('proyecto/<slug:proyecto_slug>/', views.proyecto_detail, name='proyecto_detail'),
    path('activate/<uidb64>/<token>', views.VerificationView.as_view(), name='activate'),
    path('roles/lista/',views.RolListView.as_view(),name='list_rol'),
    path('roles/create/',views.RolCreateView.as_view(),name='create_rol'),
    path('roles/update/<int:pk>/',views.RolUpdateView.as_view(),name='update_rol'),
    path('roles/delete/<int:pk>/',views.RolDeleteView.as_view(),name='delete_rol')

]
