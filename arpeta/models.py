from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
import os
import qrcode
from io import BytesIO
from phonenumber_field.modelfields import PhoneNumberField

class Camionero(models.Model):
    cedula = models.CharField(primary_key=True, max_length=10, verbose_name='Cédula')
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    apellido = models.CharField(max_length=50, verbose_name='Apellido')
    telefono = PhoneNumberField(region='VE', verbose_name='Teléfono', blank=True, null=True)
    correo = models.EmailField(max_length=100, verbose_name='Correo Electrónico', blank=True, null=True)
    direccion = models.TextField(verbose_name='Dirección', blank=True, null=True)
    autonomo = models.BooleanField(default=True, verbose_name='Autónomo')
    foto_camionero = models.ImageField(upload_to='camioneros/', blank=True, null=True, verbose_name='Foto de Perfil')

    @property
    def autonomo_texto(self):
        return "Sí" if self.autonomo else "No"

    def delete(self, *args, **kwargs):
        if self.foto_camionero and os.path.isfile(self.foto_camionero.path):
            os.remove(self.foto_camionero.path)

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Cédula: {self.cedula} - Nombre: {self.nombre} - Apellido: {self.apellido} - Autónomo: {self.autonomo_texto}"


class Camion(models.Model):
    placa = models.CharField(primary_key=True, max_length=10, verbose_name='Placa')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    alto = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Alto')
    ancho = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Ancho')
    largo = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Largo')
    foto_camion = models.ImageField(upload_to='camiones/', blank=True, null=True, verbose_name='Foto del Camión')
    codigo_qr = models.ImageField(upload_to='codigos_qr/', blank=True, null=True, verbose_name='Código QR')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.codigo_qr:
            contenido_qr = f"Placa: {self.placa}\nModelo: {self.modelo}\nDimensiones: {self.alto}x{self.ancho}x{self.largo}"
            imagen_qr = qrcode.make(contenido_qr)
            buffer = BytesIO()
            imagen_qr.save(buffer, format='PNG')
            nombre_archivo = f"qr_camion_{self.placa}.png"
            self.codigo_qr.save(nombre_archivo, ContentFile(buffer.getvalue()), save=False)
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.foto_camion and os.path.isfile(self.foto_camion.path):
            os.remove(self.foto_camion.path)
        if self.codigo_qr and os.path.isfile(self.codigo_qr.path):
            os.remove(self.codigo_qr.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Placa: {self.placa} - Modelo: {self.modelo} - Dimensiones: {self.alto} x {self.ancho} x {self.largo}"


class CamioneroCamion(models.Model):
    camionero = models.ForeignKey(Camionero, on_delete=models.CASCADE, verbose_name='Camionero')
    camion = models.ForeignKey(Camion, on_delete=models.CASCADE, verbose_name='Camión')
    fecha_asignacion = models.DateField(verbose_name='Fecha de Asignación')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['camionero', 'camion'], name='unique_camionero_camion')
        ]
        verbose_name = 'Relación Camionero-Camión'
        verbose_name_plural = 'Relaciones Camionero-Camión'

    @property
    def fecha_formateada(self):
        return self.fecha_asignacion.strftime("%d-%m-%Y")

    @property
    def estado_texto(self):
        return "Activo" if self.activo else "Inactivo"

    def __str__(self):
        return f"Camionero: {self.camionero.nombre} {self.camionero.apellido} - Camión: {self.camion.modelo} - Fecha de Asignación: {self.fecha_formateada} - Estado: {self.estado_texto}"
    