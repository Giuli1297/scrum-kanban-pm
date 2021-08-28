from django import forms
from projectmanager.models import Proyecto

class ProyectoForm(forms.ModelForm):

    class Meta:
        model = Proyecto

        fields = [
            'nombre',
            'slug',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'estado',
            'scrum_master',
            'scrum_member',
            'product_backlog',
            'sprintList',
        ]

        labels = {
            'nombre':'Nombre',
            'slug':'Slug',
            'descripcion':'Descripcion',
            'fecha_inicio':'Fecha de inicio',
            'fecha_fin':'Fecha de fin',
            'estado':'Estado',
            'scrum_master':'SCrum Master',
            'scrum_member':'Scrum Member',
            'product_backlog':'Product Backlog',
            'sprintList':'SprintList',
        }

        OPCIONES = [('PEN', 'Pendiente')]
        
        widgets = {
            'nombre':forms.TextInput(),
            'slug':forms.TextInput(),
            'descripcion':forms.TextInput(),
            'fecha_inicio':forms.DateInput(),
            'fecha_fin':forms.DateInput(),
            'estado':forms.Select(choices=OPCIONES),
            'scrum_master':forms.Select(),
            'scrum_member':forms.CheckboxSelectMultiple(),
            'product_backlog':forms.TextInput(),
            'sprintList':forms.TextInput(),
        }