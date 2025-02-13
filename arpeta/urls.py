from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    
    path('camioneros', views.camioneros, name='camioneros'),
    path('camioneros/crear_camionero', views.crear_camionero, name='crear_camionero'),
    path('camioneros/editar_camionero/<str:cedula>/', views.editar_camionero, name='editar_camionero'),
    path('camioneros/borrar_camionero/<str:cedula>/', views.borrar_camionero, name='borrar_camionero'),
    
    path('camiones', views.camiones, name='camiones'),
    path('camiones/crear_camion', views.crear_camion, name='crear_camion'),
    path('camiones/editar_camion/<str:placa>/', views.editar_camion, name='editar_camion'),
    path('camiones/borrar_camion/<str:placa>/', views.borrar_camion, name='borrar_camion'),
    
    path('camioneros_camiones', views.camioneros_camiones, name='camioneros_camiones'),
    path('camioneros_camiones/crear_camionero_camion', views.crear_camionero_camion, name='crear_camionero_camion'),
    path('camioneros_camiones/editar_camionero_camion/<int:id>/', views.editar_camionero_camion, name='editar_camionero_camion'),
    path('camioneros_camiones/borrar_camionero_camion/<int:id>/', views.borrar_camionero_camion, name='borrar_camionero_camion'),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('descargar_qr/<str:placa>/', views.descargar_qr, name='descargar_qr'),
]
