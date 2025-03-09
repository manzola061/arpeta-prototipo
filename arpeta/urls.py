from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.inicio, name='inicio'),

    path('operadores', views.operadores, name='operadores'),
    path('operadores/crear_operador', views.crear_operador, name='crear_operador'),
    path('operadores/editar_operador/<str:cedula>/', views.editar_operador, name='editar_operador'),
    path('operadores/borrar_operador/<str:cedula>/', views.borrar_operador, name='borrar_operador'),

    path('vehiculos', views.vehiculos, name='vehiculos'),
    path('vehiculos/crear_vehiculo', views.crear_vehiculo, name='crear_vehiculo'),
    path('vehiculos/editar_vehiculo/<str:placa>/', views.editar_vehiculo, name='editar_vehiculo'),
    path('vehiculos/borrar_vehiculo/<str:placa>/', views.borrar_vehiculo, name='borrar_vehiculo'),
    path('descargar_qr/<str:placa>/', views.descargar_qr, name='descargar_qr'),

    path('asignaciones', views.asignaciones, name='asignaciones'),
    path('asignaciones/crear_asignacion', views.crear_asignacion, name='crear_asignacion'),
    path('cambiar_estado/<int:id>/', views.cambiar_estado, name='cambiar_estado'),
    path("crear_tipo_material/", views.crear_tipo_material, name="crear_tipo_material"),
    path("registrar_vuelta/", views.registrar_vuelta, name="registrar_vuelta"),
    
    # Nuevo
    path('operadores/detalles/<str:cedula>/', views.detalles_operador, name='detalles_operador'),
]