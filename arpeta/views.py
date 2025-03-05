from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from .models import Operador, Vehiculo, TipoMaterial, Asignacion
from .forms import OperadorForm, VehiculoForm, AsignacionForm
import os
import json


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def inicio(request):
    return render(request, 'paginas/inicio.html')


@login_required
def operadores(request):
    operadores = Operador.objects.all().order_by('nombre')
    paginator = Paginator(operadores, 2)
    page_number = request.GET.get('page')
    operadores = paginator.get_page(page_number)
    return render(request, 'operadores/index_operador.html', {'operadores': operadores})


@login_required
def crear_operador(request):
    if request.method == "POST":
        formulario = OperadorForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('operadores')
    else:
        formulario = OperadorForm()
    return render(request, 'operadores/crear_operador.html', {'formulario': formulario})


@login_required
def editar_operador(request, cedula):
    operador = Operador.objects.get(cedula=cedula)
    formulario = OperadorForm(request.POST or None, instance=operador)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('operadores')
    return render(request, 'operadores/editar_operador.html', {'formulario': formulario})


@login_required
def borrar_operador(request, cedula):
    operador = Operador.objects.get(cedula=cedula)
    operador.delete()
    return redirect('operadores')


@login_required
def vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by('modelo')
    paginator = Paginator(vehiculos, 2)
    page_number = request.GET.get('page')
    vehiculos = paginator.get_page(page_number)
    return render(request, 'vehiculos/index_vehiculo.html', {'vehiculos': vehiculos})


@login_required
def crear_vehiculo(request):
    if request.method == "POST":
        formulario = VehiculoForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('vehiculos')
    else:
        formulario = VehiculoForm()
    return render(request, 'vehiculos/crear_vehiculo.html', {'formulario': formulario})


@login_required
def editar_vehiculo(request, placa):
    vehiculo = Vehiculo.objects.get(placa=placa)
    formulario = VehiculoForm(request.POST or None, instance=vehiculo)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('vehiculos')
    return render(request, 'vehiculos/editar_vehiculo.html', {'formulario': formulario})


@login_required
def borrar_vehiculo(request, placa):
    vehiculo = Vehiculo.objects.get(placa=placa)
    vehiculo.delete()
    return redirect('vehiculos')


@login_required
def descargar_qr(request, placa):
    try:
        placa_vehiculo = Vehiculo.objects.get(placa=placa)
        qr_path = os.path.join(settings.MEDIA_ROOT, placa_vehiculo.codigo_qr.name)
        return FileResponse(open(qr_path, 'rb'), as_attachment=True, filename=os.path.basename(qr_path))
    except (Vehiculo.DoesNotExist, FileNotFoundError):
        raise Http404("El QR no existe")


@login_required
def asignaciones(request):
    asignaciones = Asignacion.objects.all().order_by('id')
    paginator = Paginator(asignaciones, 2)
    page_number = request.GET.get('page')
    asignaciones = paginator.get_page(page_number)
    return render(request, 'asignaciones/index_asignacion.html', {'asignaciones': asignaciones})


@login_required
def crear_asignacion(request):
    formulario = AsignacionForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('asignaciones')
    return render(request, 'asignaciones/crear_asignacion.html', {'formulario': formulario})


@login_required
def editar_asignacion(request, id):
    asignacion = Asignacion.objects.get(id=id)
    formulario = AsignacionForm(request.POST or None, instance=asignacion)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('asignaciones')
    return render(request, 'asignaciones/editar_asignacion.html', {'formulario': formulario})


@login_required
def borrar_asignacion(request, id):
    asignacion = Asignacion.objects.get(id=id)
    asignacion.delete()
    return redirect('asignaciones')


@login_required
def crear_tipo_material(request):
    if request.method == "POST":
        data = json.loads(request.body)
        nombre = data.get("nombre", "").strip()
        if nombre:
            material, created = TipoMaterial.objects.get_or_create(nombre=nombre)
            return JsonResponse({"success": True, "id": material.id, "nombre": material.nombre})
    return JsonResponse({"success": False})


@login_required
def registrar_vuelta(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            placa = data.get("placa")

            vehiculo = Vehiculo.objects.get(placa=placa)

            relacion = Asignacion.objects.get(vehiculo=vehiculo)

            relacion.total_vueltas += 1
            relacion.total_material = relacion.total_vueltas * vehiculo.capacidad_carga
            relacion.save()

            return JsonResponse({
                "message": "Vuelta registrada con exito",
                "total_vueltas": relacion.total_vueltas
            }, status=200)

        except Vehiculo.DoesNotExist:
            return JsonResponse({"error": "Vehiculo no encontrado"}, status=404)
        except Asignacion.DoesNotExist:
            return JsonResponse({"error": "No hay un operador asignado a este vehiculo"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Metodo no permitido"}, status=405)