from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from .views import homepage

urlpatterns = [
    path('', homepage,name="home"),
]
