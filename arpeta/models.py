from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from phonenumber_field.modelfields import PhoneNumberField
import qrcode
import os
from io import BytesIO

# Modelo que representa a un Operador (conductor)
class Operador(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10, verbose_name='Cédula')
    nombre = models.CharField(max_length=25, verbose_name='Nombre')
    apellido = models.CharField(max_length=25, verbose_name='Apellido')
    telefono = PhoneNumberField(region='VE', verbose_name='Teléfono')
    correo = models.EmailField(max_length=100, verbose_name='Correo Electrónico')
    direccion = models.TextField(verbose_name='Dirección')
    independiente = models.BooleanField(default=True, verbose_name='Independiente')
    foto_operador = models.ImageField(upload_to='operadores/', blank=True, null=True, verbose_name='Foto del Operador')

    # Propiedad que devuelve "Si" o "No" dependiendo del valor del campo independiente
    @property
    def independiente_texto(self):
        return "Si" if self.independiente else "No"

    # Método para eliminar un operador, asegurándose de eliminar también su foto del sistema de archivos
    def delete(self, *args, **kwargs):
        if self.foto_operador and os.path.isfile(self.foto_operador.path):
            os.remove(self.foto_operador.path)
        super().delete(*args, **kwargs)

    # Método para representar el objeto Operador como una cadena de texto
    def __str__(self):
        return f"Cédula: {self.cedula} - Operador: {self.nombre} {self.apellido}"


# Modelo que representa una Marca de vehículo
class Marca(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Marca')

    # Método para representar el objeto Marca como una cadena de texto
    def __str__(self):
        return self.nombre


# Modelo que representa un Modelo de vehículo, asociado a una Marca
class Modelo(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Modelo')
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, verbose_name='Marca')

    # Método para representar el objeto Modelo como una cadena de texto
    def __str__(self):
        return f"{self.marca.nombre} - {self.nombre}"


# Modelo que representa un Vehículo
class Vehiculo(models.Model):
    placa = models.CharField(primary_key=True, max_length=10, verbose_name="Placa")
    modelo = models.ForeignKey(Modelo, on_delete=models.CASCADE, verbose_name="Modelo")
    alto = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Alto (m)")
    ancho = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Ancho (m)")
    largo = models.DecimalField(decimal_places=2, default=0.00, max_digits=4, verbose_name="Largo (m)")
    capacidad_carga = models.DecimalField(decimal_places=2, default=0.00, max_digits=5, verbose_name="Capacidad de Carga (m³)")
    foto_vehiculo = models.ImageField(upload_to="vehiculos/", blank=True, null=True, verbose_name="Foto del Vehículo")
    codigo_qr = models.ImageField(upload_to="codigos_qr/", verbose_name="Código QR")

    # Método para guardar el vehículo, calculando la capacidad de carga y generando el código QR si no existe
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

    # Método para eliminar un vehículo, asegurándose de eliminar también su foto y código QR del sistema de archivos
    def delete(self, *args, **kwargs):
        if self.foto_vehiculo and os.path.isfile(self.foto_vehiculo.path):
            os.remove(self.foto_vehiculo.path)
        if self.codigo_qr and os.path.isfile(self.codigo_qr.path):
            os.remove(self.codigo_qr.path)
        super().delete(*args, **kwargs)

    # Método para representar el objeto Vehículo como una cadena de texto
    def __str__(self):
        return f"Placa: {self.placa} - Vehíuculo: {self.modelo.marca} - {self.modelo.nombre}"


# Modelo que representa un Tipo de Material
class TipoMaterial(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name='Tipo de Material')

    # Método para representar el objeto TipoMaterial como una cadena de texto
    def __str__(self):
        return self.nombre


# Modelo que representa una Asignación de un vehículo a un operador
class Asignacion(models.Model):
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, verbose_name='Operador')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name='Vehículo')
    fecha_asignacion = models.DateField(verbose_name='Fecha de Asignación')
    tipo_material = models.ForeignKey(TipoMaterial, on_delete=models.CASCADE, verbose_name="Tipo de Material", null=True, blank=True)
    total_vueltas = models.IntegerField(default=0, verbose_name="Total de Vueltas")
    total_material = models.DecimalField(decimal_places=2, default=0.00, max_digits=6, verbose_name='Total de Material (m³)')
    estado = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        # Restricción para asegurar que no haya asignaciones duplicadas para el mismo operador, vehículo y fecha
        constraints = [
            models.UniqueConstraint(fields=['operador', 'vehiculo', 'fecha_asignacion'], name='unique_operador_vehiculo_fecha')
        ]
        verbose_name = 'Asignacion'
        verbose_name_plural = 'Asignaciones'

    # Método para guardar la asignación, calculando el total de material transportado
    def save(self, *args, **kwargs):
        if self.vehiculo:
            self.total_material = self.total_vueltas * self.vehiculo.capacidad_carga
        super().save(*args, **kwargs)

    # Propiedad que devuelve la fecha de asignación formateada como "dd-mm-yyyy"
    @property
    def fecha_formateada(self):
        return self.fecha_asignacion.strftime("%d-%m-%Y")

    # Propiedad que devuelve "Activo" o "Inactivo" dependiendo del valor del campo estado
    @property
    def estado_texto(self):
        return "Activo" if self.estado else "Inactivo"

    # Método para representar el objeto Asignacion como una cadena de texto
    def __str__(self):
        return f"Cédula Operador: {self.operador.cedula} - Placa Vehículo: {self.vehiculo.placa} - Fecha Asignación: {self.fecha_formateada} - Tipo Material: {self.tipo_material.nombre} - Total Vueltas: {self.total_vueltas} - Total Material: {self.total_material} m³ - Estado: {self.estado_texto}"