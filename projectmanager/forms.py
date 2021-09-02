from django.forms import *

from django.contrib.auth.models import User,Group
from .models import rol


class RolForm(ModelForm):
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
            'name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                }
            ),
            'permissions': CheckboxSelectMultiple(attrs={

            }),

        }
        exclude = ['last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = 'username', 'groups'
        widgets = {

            'username': TextInput(
                attrs={
                    'placeholder': 'Ingrese su username',
                }
            ),
            'groups': SelectMultiple(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'multiple': 'multiple'
            })
        }
        exclude = ['user_permissions', 'last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

