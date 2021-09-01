from django import forms
from projectmanager.models import Proyecto


class ProyectoForm(forms.ModelForm):
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
