from django import forms
from projectmanager.models import Proyecto


class ProyectoForm(forms.ModelForm):
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
    class Meta:
        model = Proyecto

        fields = [
            'scrum_member',
        ]

        labels = {
            'scrum_member': 'Scrum Members'
        }

        widgets = {
            'scrum_member': forms.CheckboxSelectMultiple(attrs={'class': 'check-label'}),
        }
