from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from .models import Operador, Vehiculo, TipoMaterial, Asignacion
from .forms import OperadorForm, VehiculoForm, AsignacionForm
import os
import json
import qrcode
from io import BytesIO

# Vista para el inicio de sesión
def login_view(request):
    if request.method == 'POST':
        # Si la solicitud es POST, procesa el formulario de autenticación
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Obtiene el correo y la contraseña del formulario
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Autentica al usuario
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Si el usuario es válido, inicia sesión y redirige a la página de inicio
                login(request, user)
                return redirect('inicio')
            else:
                # Si la autenticación falla, muestra un mensaje de error
                messages.error(request, "Correo o contraseña incorrectos.")
        else:
            # Si el formulario no es válido, muestra un mensaje de error
            messages.error(request, "Correo o contraseña incorrectos.")
    else:
        # Si la solicitud no es POST, muestra el formulario de inicio de sesión
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Vista para el cierre de sesión
def logout_view(request):
    # Cierra la sesión del usuario y redirige a la página de inicio de sesión
    logout(request)
    return redirect('login')


# Vista para la página de inicio (requiere autenticación)
@login_required
def inicio(request):
    return render(request, 'paginas/inicio.html')


# Vista para listar operadores (requiere autenticación)
@login_required
def operadores(request):
    # Obtiene todos los operadores ordenados por nombre
    operadores = Operador.objects.all().order_by('nombre')
    # Pagina los resultados (1 operador por página)
    paginator = Paginator(operadores, 1)
    page_number = request.GET.get('page')
    operadores = paginator.get_page(page_number)
    return render(request, 'operadores/index_operador.html', {'operadores': operadores})


# Vista para crear un operador (requiere autenticación)
@login_required
def crear_operador(request):
    if request.method == "POST":
        # Si la solicitud es POST, procesa el formulario de operador
        formulario = OperadorForm(request.POST, request.FILES)
        if formulario.is_valid():
            # Si el formulario es válido, guarda el operador y redirige a la lista de operadores
            formulario.save()
            return redirect('operadores')
    else:
        # Si la solicitud no es POST, muestra el formulario vacío
        formulario = OperadorForm()
    return render(request, 'operadores/crear_operador.html', {'formulario': formulario})


# Vista para editar un operador (requiere autenticación)
@login_required
def editar_operador(request, cedula):
    # Obtiene el operador por su cédula
    operador = Operador.objects.get(cedula=cedula)
    # Crea un formulario con los datos del operador
    formulario = OperadorForm(request.POST or None, instance=operador)
    if formulario.is_valid() and request.POST:
        # Si el formulario es válido y la solicitud es POST, guarda los cambios y redirige a la lista de operadores
        formulario.save()
        return redirect('operadores')
    return render(request, 'operadores/editar_operador.html', {'formulario': formulario})


# Vista para borrar un operador (requiere autenticación)
@login_required
def borrar_operador(request, cedula):
    # Obtiene el operador por su cédula y lo elimina
    operador = Operador.objects.get(cedula=cedula)
    operador.delete()
    return redirect('operadores')


# Vista para listar vehículos (requiere autenticación)
@login_required
def vehiculos(request):
    # Obtiene todos los vehículos ordenados por modelo
    vehiculos = Vehiculo.objects.all().order_by('modelo')
    # Pagina los resultados (1 vehículo por página)
    paginator = Paginator(vehiculos, 1)
    page_number = request.GET.get('page')
    vehiculos = paginator.get_page(page_number)
    return render(request, 'vehiculos/index_vehiculo.html', {'vehiculos': vehiculos})


# Vista para crear un vehículo (requiere autenticación)
@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        # Si la solicitud es POST, procesa el formulario de vehículo
        formulario = VehiculoForm(request.POST, request.FILES)
        if formulario.is_valid():
            # Si el formulario es válido, guarda el vehículo y redirige a la lista de vehículos
            formulario.save()
            return redirect('vehiculos')
    else:
        # Si la solicitud no es POST, muestra el formulario vacío
        formulario = VehiculoForm()
    return render(request, 'vehiculos/crear_vehiculo.html', {'formulario': formulario})


# Vista para editar un vehículo (requiere autenticación)
@login_required
def editar_vehiculo(request, placa):
    # Obtiene el vehículo por su placa
    vehiculo = Vehiculo.objects.get(placa=placa)
    # Crea un formulario con los datos del vehículo
    formulario = VehiculoForm(request.POST or None, instance=vehiculo)
    if formulario.is_valid() and request.POST:
        # Si el formulario es válido y la solicitud es POST, guarda los cambios y redirige a la lista de vehículos
        formulario.save()
        return redirect('vehiculos')
    return render(request, 'vehiculos/editar_vehiculo.html', {'formulario': formulario})


# Vista para borrar un vehículo (requiere autenticación)
@login_required
def borrar_vehiculo(request, placa):
    # Obtiene el vehículo por su placa y lo elimina
    vehiculo = Vehiculo.objects.get(placa=placa)
    vehiculo.delete()
    return redirect('vehiculos')


# Vista para descargar el código QR de un vehículo (requiere autenticación)
@login_required
def descargar_qr(request, placa):
    # Obtiene el vehículo por su placa
    placa_vehiculo = get_object_or_404(Vehiculo, placa=placa)

    # Genera el código QR en memoria
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(placa_vehiculo.placa)  # Usa la placa como dato para el QR
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Devuelve el archivo QR como una respuesta de descarga
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="{placa_vehiculo.placa}.png"'
    return response


# Vista para listar asignaciones (requiere autenticación)
@login_required
def asignaciones(request):
    # Obtiene todas las asignaciones ordenadas por ID
    asignaciones = Asignacion.objects.all().order_by('id')
    # Pagina los resultados (1 asignación por página)
    paginator = Paginator(asignaciones, 1)
    page_number = request.GET.get('page')
    asignaciones = paginator.get_page(page_number)
    return render(request, 'asignaciones/index_asignacion.html', {'asignaciones': asignaciones})


# Vista para crear una asignación (requiere autenticación)
@login_required
def crear_asignacion(request):
    if request.method == 'POST':
        # Si la solicitud es POST, procesa el formulario de asignación
        formulario = AsignacionForm(request.POST)
        if formulario.is_valid():
            # Si el formulario es válido, guarda la asignación con la fecha actual y redirige a la lista de asignaciones
            asignacion = formulario.save(commit=False)
            asignacion.fecha_asignacion = timezone.localtime(timezone.now()).date()
            asignacion.save()
            return redirect('asignaciones')
    else:
        # Si la solicitud no es POST, muestra el formulario vacío
        formulario = AsignacionForm()
    return render(request, 'asignaciones/crear_asignacion.html', {'formulario': formulario})


# Vista para cambiar el estado de una asignación (requiere autenticación)
@login_required
def cambiar_estado(request, id):
    # Obtiene la asignación por su ID o devuelve un error 404 si no existe
    asignacion = get_object_or_404(Asignacion, id=id)
    # Cambia el estado de la asignación (activo/inactivo)
    asignacion.estado = not asignacion.estado
    asignacion.save()
    return redirect('asignaciones')


# Vista para crear un tipo de material (requiere autenticación)
@login_required
def crear_tipo_material(request):
    if request.method == "POST":
        # Si la solicitud es POST, procesa los datos JSON
        data = json.loads(request.body)
        nombre = data.get("nombre", "").strip()
        if nombre:
            # Si el nombre no está vacío, crea o obtiene el tipo de material
            material, creado = TipoMaterial.objects.get_or_create(nombre=nombre)
            return JsonResponse({"success": True, "id": material.id, "nombre": material.nombre})
    return JsonResponse({"success": False})


# Vista para registrar una vuelta (requiere autenticación)
@login_required
def registrar_vuelta(request):
    if request.method == "POST":
        try:
            # Si la solicitud es POST, procesa los datos JSON
            data = json.loads(request.body)
            placa = data.get("placa")
            # Obtiene el vehículo por su placa
            vehiculo = Vehiculo.objects.get(placa=placa)
            # Obtiene la asignación relacionada con el vehículo
            relacion = Asignacion.objects.get(vehiculo=vehiculo)
            # Incrementa el total de vueltas y recalcula el total de material
            relacion.total_vueltas += 1
            relacion.total_material = relacion.total_vueltas * vehiculo.capacidad_carga
            relacion.save()
            return JsonResponse({
                "message": "Vuelta registrada con éxito.",
                "total_vueltas": relacion.total_vueltas
            }, status=200)
        except Vehiculo.DoesNotExist:
            return JsonResponse({"error": "Vehículo no encontrado."}, status=404)
        except Asignacion.DoesNotExist:
            return JsonResponse({"error": "No hay un operador asignado a este vehículo."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Método no permitido."}, status=405)


@login_required
def detalles_operador(request, cedula):
    operador = Operador.objects.get(cedula=cedula)
    data = {
        'cedula': operador.cedula,
        'nombre': operador.nombre,
        'apellido': operador.apellido,
        'telefono': str(operador.telefono),
        'correo': operador.correo,
        'direccion': operador.direccion,
        'independiente_texto': operador.independiente_texto,
        'foto_operador': operador.foto_operador.url if operador.foto_operador else None,
    }
    return JsonResponse(data)