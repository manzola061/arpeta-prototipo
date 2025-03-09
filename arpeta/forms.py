from django import forms
from .models import Operador, Vehiculo, Asignacion

# Formulario para el modelo Operador
class OperadorForm(forms.ModelForm):
    class Meta:
        # Especifica el modelo asociado al formulario
        model = Operador
        # Incluye todos los campos del modelo en el formulario
        fields = '__all__'


# Formulario para el modelo Vehiculo
class VehiculoForm(forms.ModelForm):
    class Meta:
        # Especifica el modelo asociado al formulario
        model = Vehiculo
        # Excluye los campos 'capacidad_carga' y 'codigo_qr' del formulario
        # Estos campos se calculan automáticamente y no deben ser editados manualmente
        exclude = ['capacidad_carga', 'codigo_qr']


# Formulario para el modelo Asignacion
class AsignacionForm(forms.ModelForm):
    class Meta:
        # Especifica el modelo asociado al formulario
        model = Asignacion
        # Excluye los campos 'fecha_asignacion', 'total_vueltas', 'total_material' y 'estado' del formulario
        # Estos campos se gestionan automáticamente o se calculan en tiempo real
        exclude = ['fecha_asignacion', 'total_vueltas', 'total_material', 'estado']