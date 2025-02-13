from django import forms
from .models import Camionero, Camion, CamioneroCamion

class CamioneroForm(forms.ModelForm):
    class Meta:
        model = Camionero
        fields = '__all__'

class CamionForm(forms.ModelForm):
    class Meta:
        model = Camion
        fields = '__all__'

class CamioneroCamionForm(forms.ModelForm):
    class Meta:
        model = CamioneroCamion
        fields = '__all__'
        widgets = {
            'fecha_asignacion': forms.DateInput(attrs={'type': 'date'}),
        }
