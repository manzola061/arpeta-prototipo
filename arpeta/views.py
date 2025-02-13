from django.shortcuts import render, redirect
from .models import Camionero, Camion, CamioneroCamion
from .forms import CamioneroForm, CamionForm, CamioneroCamionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.conf import settings
import os
from django.core.paginator import Paginator


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
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
def camioneros(request):
    camioneros = Camionero.objects.all().order_by('nombre')
    paginator = Paginator(camioneros, 2)
    page_number = request.GET.get('page')
    camioneros = paginator.get_page(page_number)
    return render(request, 'camioneros/index_camionero.html', {'camioneros': camioneros})


@login_required
def crear_camionero(request):
    if request.method == "POST":
        formulario = CamioneroForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('camioneros')
    else:
        formulario = CamioneroForm()
    return render(request, 'camioneros/crear_camionero.html', {'formulario': formulario})


@login_required
def editar_camionero(request, cedula):
    camionero = Camionero.objects.get(cedula=cedula)
    formulario = CamioneroForm(request.POST or None, instance=camionero)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('camioneros')
    return render(request, 'camioneros/editar_camionero.html', {'formulario': formulario})


@login_required
def borrar_camionero(request, cedula):
    camionero = Camionero.objects.get(cedula=cedula)
    camionero.delete()
    return redirect('camioneros')


@login_required
def camiones(request):
    camiones = Camion.objects.all()
    paginator = Paginator(camiones, 2)
    page_number = request.GET.get('page')
    camiones = paginator.get_page(page_number)
    return render(request, 'camiones/index_camion.html', {'camiones': camiones})


@login_required
def crear_camion(request):
    if request.method == "POST":
        formulario = CamionForm(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            return redirect('camiones')
    else:
        formulario = CamionForm()
    return render(request, 'camiones/crear_camion.html', {'formulario': formulario})


@login_required
def editar_camion(request, placa):
    camion = Camion.objects.get(placa=placa)
    formulario = CamionForm(request.POST or None, instance=camion)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('camiones')
    return render(request, 'camiones/editar_camion.html', {'formulario': formulario})


@login_required
def borrar_camion(request, placa):
    camion = Camion.objects.get(placa=placa)
    camion.delete()
    return redirect('camiones')


@login_required
def camioneros_camiones(request):
    camioneros_camiones = CamioneroCamion.objects.all().order_by('id')
    paginator = Paginator(camioneros_camiones, 2)
    page_number = request.GET.get('page')
    camioneros_camiones = paginator.get_page(page_number)
    return render(request, 'camioneros_camiones/index_camionero_camion.html', {'camioneros_camiones': camioneros_camiones})


@login_required
def crear_camionero_camion(request):
    formulario = CamioneroCamionForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('camioneros_camiones')
    return render(request, 'camioneros_camiones/crear_camionero_camion.html', {'formulario': formulario})


@login_required
def editar_camionero_camion(request, id):
    camionero_camion = CamioneroCamion.objects.get(id=id)
    formulario = CamioneroCamionForm(request.POST or None, instance=camionero_camion)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('camioneros_camiones')
    return render(request, 'camioneros_camiones/editar_camionero_camion.html', {'formulario': formulario})


@login_required
def borrar_camionero_camion(request, id):
    camionero_camion = CamioneroCamion.objects.get(id=id)
    camionero_camion.delete()
    return redirect('camioneros_camiones')


@login_required
def descargar_qr(request, placa):
    try:
        placa_camion = Camion.objects.get(placa=placa)
        qr_path = os.path.join(settings.MEDIA_ROOT, placa_camion.codigo_qr.name)
        return FileResponse(open(qr_path, 'rb'), as_attachment=True, filename=os.path.basename(qr_path))
    except (Camion.DoesNotExist, FileNotFoundError):
        raise Http404("El QR no existe.")
