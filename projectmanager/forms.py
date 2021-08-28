from django.forms import *

from django.contrib.auth.models import User,Group
from .models import rol


class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = rol
        fields = ['name','permissions']
        labels = {
            'name': 'Nombre del rol',
            'permissions': 'Seleccione permisos'

        }
        widgets = {
            'name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                }
            ),
            'permissions': CheckboxSelectMultiple(attrs={

            })
        }
        exclude = ['last_login', 'date_joined', 'is_superuser', 'is_active', 'is_staff']

