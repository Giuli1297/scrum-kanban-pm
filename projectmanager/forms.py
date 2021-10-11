from django import forms
from django.db import models
from projectmanager.models import *
from django.contrib.auth.models import User
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q


class ProyectoForm(forms.ModelForm):
    """
       Clase de formulario para el modelo Proyecto

    """
    scrum_master = forms.ModelChoiceField(
        queryset=User.objects.filter(~Q(username='AnonymousUser') & ~Q(username='admin')))

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


class AgregarScrumMemberForm(forms.Form):
    """
        Clase de formulario para editar datos de un proyecto
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(AgregarScrumMemberForm, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['scrum_member'].queryset = User.objects.filter(
            ~Q(proyecto_asignado=self.proyecto) & ~Q(username='AnonymousUser') & ~Q(username='admin'))

    scrum_member = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'check-label'}))
    lunes = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), initial=0)
    martes = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), initial=0)
    miercoles = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), initial=0)
    jueves = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), initial=0)
    viernes = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}), initial=0)


class QuitarScrumMemberForm(forms.Form):
    """
        Clase de formulario para editar datos de un proyecto
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(QuitarScrumMemberForm, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['scrum_member'].queryset = User.objects.filter(
            Q(proyecto_asignado=self.proyecto) & ~Q(username='AnonymousUser') & ~Q(username='admin'))

    scrum_member = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'check-label'}))


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
    """
        Clase formulario para la creacion de rol a nivel de proyecto
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(CrearRolProyectoForm, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['scrum_members'].queryset = User.objects.filter(Q(proyecto_asignado=self.proyecto))
        self.fields['permisos'].queryset = Permission.objects.filter(
            Q(content_type__model='proyecto', content_type__app_label='projectmanager', ))

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
    """
        Clase formulario para la creacion de User Stories de proyecto
    """
    descripción_de_user_story = forms.CharField(max_length=100, widget=forms.Textarea(attrs={
        'class': 'form-control'
    }))
    documentación =  forms.CharField(label='Requisitos para pasar a Done',max_length=100, widget=forms.Textarea(attrs={
        'class': 'form-control'
    }))
    prioridad_1_al_10 = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control'
    }))


class ImportarRolProyectoForm(forms.Form):
    """
        Clase formulario para la importacion de un rol de prouecto de un proyecto a otro
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(ImportarRolProyectoForm, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.nombres = []
        for rol in self.proyecto.roles.all():
            self.nombres.append(rol.copied_from)
        self.fields['roles'].queryset = Rol.objects.filter(
            ~Q(proyecto=self.proyecto) & Q(tipo='proyecto') & ~Q(related_group__name__in=self.nombres))

    roles = forms.ModelMultipleChoiceField(queryset=None,
                                           widget=forms.CheckboxSelectMultiple(attrs={'class': 'check-label'}))


class SprintFormCreate(forms.Form):
    """
        Clase formulario para la creacion de spriat
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(SprintFormCreate, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['UserStorys'].queryset = UserStory.objects.filter(proyecto=self.proyecto)

    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    UserStorys = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'check-label'
        }))


class SprintFormUpdate(forms.Form):
    """
        Clase formulario para la actualizacion de un sprint
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(SprintFormUpdate, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['UserStorys'].queryset = UserStory.objects.filter(proyecto=self.proyecto)

    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    UserStorys = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'check-label'
        }))


class AsignarDesarrolladorUs(forms.Form):
    """
        Clase formulario para la asignacion de un usuario a un User Story
    """

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug')
        super(AsignarDesarrolladorUs, self).__init__(*args, **kwargs)
        self.proyecto = Proyecto.objects.get(slug=self.slug)
        self.fields['desarrolladorAsignado'].queryset = User.objects.filter(proyecto_asignado=self.proyecto)

    desarrolladorAsignado = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'check-label'
        }))


class AsignarYEstimarUserStoryForm(forms.Form):
    """
        Clase formulario para la esstimacion y asignacion de de User Story a un desarrollador
    """

    def __init__(self, *args, **kwargs):
        self.usPk = kwargs.pop('usPk')
        super(AsignarYEstimarUserStoryForm, self).__init__(*args, **kwargs)
        self.ustory = UserStory.objects.get(pk=self.usPk)
        self.fields['scrum_member_asignado'].queryset = User.objects.filter(proyecto_asignado=self.ustory.proyecto)

    scrum_member_asignado = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'check-label'
        }))

    horas_estimadas = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class PlanningPokerSMemberForm(forms.Form):
    """
        Clase formulario para el planning poker
    """
    horas_estimadas = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class EstimacionSprint(forms.Form):
    """
        Clase formulario para la estimacion de un sprint de proyecto
    """

    dias_estimados = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                        label='Dias Laborales Estimados')


class RegistroActividadForm(forms.Form):
    descripcion = forms.CharField(max_length=5000, widget=forms.Textarea(attrs={
        'class': 'form-control', 'rows': '4'
    }))
    horas = forms.FloatField(widget=forms.NumberInput(attrs={
        'class': 'form-control'
    }))


class RealizarQAUSForm(forms.Form):
    comentario = forms.CharField(max_length=255, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': '4'
    }))
    aceptar = forms.ChoiceField(choices=(('si', 'Aceptar'), ('no', 'Rechazar')), widget=forms.Select(attrs={
        'class': 'check-label'
    }))

