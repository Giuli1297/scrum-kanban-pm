from django import forms

from projectmanager.models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q


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
        ]

        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripcion',
            'scrum_master': 'Scrum Master',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'scrum_master': forms.Select(attrs={'class': 'regDropDown'}),
        }


class ProyectoEditarSMForm(forms.ModelForm):
    """
           Clase de formulario para editar datos de un proyecto
    """

    class Meta:
        model = Proyecto

        fields = [
            'scrum_member',

        ]

        labels = {
            'scrum_member': 'Scrum Members',


        }

        widgets = {
            'scrum_member': forms.CheckboxSelectMultiple(attrs={'class': 'check-label'}),

        }


class ActualizarUsuarioForm(forms.ModelForm):
    """
        Formulario para la actualizacion de datos de usuario

    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }


class RolForm(forms.ModelForm):
    """
           Clase de formulario para el modelo Rol

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permissions"].queryset = Permission.objects.filter(
            Q(content_type__app_label='projectmanager', content_type__model='rol') |
            Q(content_type__app_label='projectmanager', content_type__model='proyecto'))
        # self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = Group
        fields = ['name', 'permissions']
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


class UserFormDelete(forms.ModelForm):
    """
           Clase de formulario para eliminar rol del User
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



class CrearRolProyectoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(CrearRolProyectoForm, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['scrum_members'].queryset = User.objects.filter(Q(proyecto_asignado=self.proyecto))
        self.fields['permisos'].queryset = Permission.objects.filter(
            Q(content_type__model='proyecto'))

    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    descripcion = forms.CharField(max_length=255,
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))
    permisos = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'check-label'
        }))
    scrum_members = forms.ModelMultipleChoiceField(queryset=None, required=False,
                                                   widget=forms.CheckboxSelectMultiple(attrs={
                                                       'class': 'check-label'
                                                   }))


class ProyectoUs(forms.Form):

    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    descripcion = forms.CharField(max_length=100, widget=forms.Textarea(attrs={
        'class': 'form-control'
    }))



class ImportarRolProyectoForm(forms.Form):
    roles = forms.ModelMultipleChoiceField(queryset=Rol.objects.filter(Q(tipo='proyecto')),
                                           widget=forms.CheckboxSelectMultiple(attrs={'class': 'check-label'}))
1
