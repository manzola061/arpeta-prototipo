from django.contrib import admin
from .models import Camionero, Camion, CamioneroCamion

admin.site.register(Camionero)
admin.site.register(Camion)
admin.site.register(CamioneroCamion)