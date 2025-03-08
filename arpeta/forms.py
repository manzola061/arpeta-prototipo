from django import forms
from .models import Operador, Vehiculo, Asignacion

class OperadorForm(forms.ModelForm):
    class Meta:
        model = Operador
        fields = '__all__'

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = '__all__'

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        exclude = ['fecha_asignacion', 'total_vueltas', 'total_material', 'estado']