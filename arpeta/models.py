from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
import os
import qrcode
from io import BytesIO
from phonenumber_field.modelfields import PhoneNumberField

class Operador(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10, verbose_name='Cédula')
    nombre = models.CharField(max_length=25, verbose_name='Nombre')
    apellido = models.CharField(max_length=25, verbose_name='Apellido')
    telefono = PhoneNumberField(blank=True, null=True, region='VE', verbose_name='Teléfono')
    correo = models.EmailField(blank=True, null=True, max_length=100, verbose_name='Correo Electrónico')
    direccion = models.TextField(blank=True, null=True, verbose_name='Dirección')
    independiente = models.BooleanField(default=True, verbose_name='Independiente')
    foto_operador = models.ImageField(upload_to='operadores/', blank=True, null=True, verbose_name='Foto del Operador')

    @property
    def independiente_texto(self):
        return "Si" if self.independiente else "No"

    def delete(self, *args, **kwargs):
        if self.foto_operador and os.path.isfile(self.foto_operador.path):
            os.remove(self.foto_operador.path)

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Cédula: {self.cedula} - Operador: {self.nombre} {self.apellido}"


class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Marca')

    def __str__(self):
        return self.nombre


class Modelo(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Modelo')
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, verbose_name='Marca')

    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"


class Vehiculo(models.Model):
    placa = models.CharField(primary_key=True, max_length=10, verbose_name="Placa")
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE, verbose_name="Modelo")
    alto = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Alto (m)")
    ancho = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Ancho (m)")
    largo = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Largo (m)")
    capacidad_carga = models.DecimalField(decimal_places=2, default=0.00, editable=False, max_digits=5, verbose_name="Capacidad de Carga (m³)")
    foto_vehiculo = models.ImageField(upload_to="vehiculos/", blank=True, null=True, verbose_name="Foto del Vehículo")
    codigo_qr = models.ImageField(upload_to="codigos_qr/", blank=True, null=True, verbose_name="Código QR")

    def save(self, *args, **kwargs):
        self.capacidad_carga = float(self.alto) * float(self.ancho) * float(self.largo)
        super().save(*args, **kwargs)

        if not self.codigo_qr:
            contenido_qr = self.placa
            imagen_qr = qrcode.make(contenido_qr)
            buffer = BytesIO()
            imagen_qr.save(buffer, format="PNG")
            nombre_archivo = f"qr_vehiculo_{self.placa}.png"
            self.codigo_qr.save(nombre_archivo, ContentFile(buffer.getvalue()), save=False)
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.foto_vehiculo and os.path.isfile(self.foto_vehiculo.path):
            os.remove(self.foto_vehiculo.path)
        if self.codigo_qr and os.path.isfile(self.codigo_qr.path):
            os.remove(self.codigo_qr.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Placa: {self.placa} - Vehíuculo: {self.modelo.marca} {self.modelo.nombre} - Capacidad de Carga: {self.capacidad_carga} m³"


class TipoMaterial(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Tipo de Material')

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, verbose_name='Operador')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name='Vehículo')
    fecha_asignacion = models.DateField(verbose_name='Fecha de Asignación')
    tipo_material = models.ForeignKey(TipoMaterial, on_delete=models.CASCADE, verbose_name="Tipo de Material", null=True, blank=True)
    total_vueltas = models.IntegerField(default=0, verbose_name="Total de Vueltas")
    total_material = models.DecimalField(decimal_places=2, default=0.00, max_digits=6, verbose_name='Total de Material (m³)')
    estado = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['operador', 'vehiculo', 'fecha_asignacion'], name='unique_operador_vehiculo_fecha')
        ]
        verbose_name = 'Asignacion'
        verbose_name_plural = 'Asignaciones'

    def save(self, *args, **kwargs):
        if self.vehiculo:
            self.total_material = self.total_vueltas * self.vehiculo.capacidad_carga
        super().save(*args, **kwargs)

    @property
    def fecha_formateada(self):
        return self.fecha_asignacion.strftime("%d-%m-%Y")

    @property
    def estado_texto(self):
        return "Activo" if self.estado else "Inactivo"

    def __str__(self):
        return f"Cédula Operador: {self.operador.cedula} - Placa Vehículo: {self.vehiculo.placa} - Fecha Asignación: {self.fecha_formateada} - Tipo Material: {self.tipo_material.nombre} - Total Vueltas: {self.total_vueltas} - Total Material: {self.total_material} m³ - Estado: {self.estado_texto}"