
from django import forms
from projectmanager.models import Proyecto
from django.contrib.auth.models import User,Group
from .models import rol


class ProyectoForm(forms.ModelForm):
    """
       Clase de formulario para el modelo Proyecto

    """
    class Meta:
        model = Proyecto

        fields = [
            'nombre',
            'descripcion',
            'scrum_master',
            'scrum_member',
        ]

        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripcion',
            'scrum_master': 'Scrum Master',
            'scrum_member': 'Scrum Member',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'scrum_master': forms.Select(attrs={'class':'regDropDown'}),
            'scrum_member': forms.CheckboxSelectMultiple(attrs={'class': 'check-label'}),
        }

class RolForm(forms.ModelForm):
    """
           Clase de formulario para el modelo Rol

        """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = rol
        fields = ['name','permissions']
        labels = {
            'name': 'Nombre del rol',
            'permissions': 'Seleccione permisos',


        }
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                }
            ),
            'permissions': forms.CheckboxSelectMultiple(attrs={

            }),

        }
        exclude = ['last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

class UserForm(forms.ModelForm):
    """
           Clase de formulario para el modelo User

        """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = 'username', 'groups'
        widgets = {

            'username': forms.TextInput(
                attrs={
                    'placeholder': 'Ingrese su username',
                }
            ),
            'groups': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'multiple': 'multiple'
            })
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

