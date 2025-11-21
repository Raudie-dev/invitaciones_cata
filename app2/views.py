from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import User_admin
from .crud import (
    crear_invitacion, obtener_invitaciones, eliminar_invitacion, actualizar_invitacion,
    crear_mesa, obtener_mesas, eliminar_mesa, actualizar_mesa,
    crear_invitado, obtener_invitados, eliminar_invitado, actualizar_invitado
)
from app1.models import Ubicacion, Invitacion, FechaEvento, Invitado, Playlist, Mesa
from datetime import date
from django.http import HttpResponse
import csv

def login(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        password = request.POST.get('password', '')

        try:
            user = User_admin.objects.get(nombre=nombre)
            if user.bloqueado:
                messages.error(request, 'Usuario bloqueado')
            elif user.password == password or check_password(password, user.password):
                request.session['user_admin_id'] = user.id
                return redirect('dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta')
            return render(request, 'login.html')
        except User_admin.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
            return render(request, 'login.html')

    return render(request, 'login.html')

def dashboard(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return redirect('login')

    total_invitaciones = Invitacion.objects.count()
    total_invitados = Invitado.objects.count()
    invitaciones_confirmadas = Invitacion.objects.filter(confirmada=True).count()
    invitados_confirmados = Invitado.objects.filter(confirmado=True).count()

    return render(request, 'dashboard.html', {
        'total_invitaciones': total_invitaciones,
        'total_invitados': total_invitados,
        'invitaciones_confirmadas': invitaciones_confirmadas,
        'invitados_confirmados': invitados_confirmados,
    })

def crear_invitacion_mesa(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return redirect('login')
    
    fecha_evento, creado = FechaEvento.objects.get_or_create(
        id=1,
        defaults={'fecha': date.today()}
    )
    
    if request.method == 'POST':
        # Crear invitación con invitados y mesas
        if 'crear_invitacion' in request.POST:
            nombre = request.POST.get('nombre_invitacion', '').strip()
            invitados_ids = request.POST.getlist('invitados_invitacion')
            mesas_ids = request.POST.getlist('mesas_invitacion')

            # Usar fecha global y ubicación global definidas en FechaEvento
            fecha = fecha_evento.fecha.isoformat() if fecha_evento and fecha_evento.fecha else None
            ubicacion_global = fecha_evento.ubicacion
            ubicacion_id = ubicacion_global.id if ubicacion_global else None

            if not ubicacion_id:
                # Fallback: si existe exactamente una ubicación, usarla como global automáticamente
                try:
                    unica_ubicacion = Ubicacion.objects.get()
                    fecha_evento.ubicacion = unica_ubicacion
                    fecha_evento.save()
                    ubicacion_id = unica_ubicacion.id
                    messages.info(request, f'Se estableció automáticamente la ubicación global: {unica_ubicacion.nombre}.')
                except Ubicacion.DoesNotExist:
                    messages.error(request, 'Debe definir una ubicación global antes de crear invitaciones.')
                except Ubicacion.MultipleObjectsReturned:
                    messages.error(request, 'Hay múltiples ubicaciones. Selecciona una como ubicación global antes de crear invitaciones.')

            if ubicacion_id and not nombre:
                messages.error(request, 'El nombre de la invitación es obligatorio.')
            elif ubicacion_id and nombre:
                # Validar invitados únicos: no permitir invitados ya asignados a otra invitación
                invitados_invalidos = []
                for iid in invitados_ids:
                    if Invitacion.objects.filter(invitados__id=iid).exists():
                        invitados_invalidos.append(iid)

                if invitados_invalidos:
                    messages.error(request, 'Uno o más invitados seleccionados ya pertenecen a otra invitación y fueron omitidos.')
                    # Remover los inválidos de la lista final
                    invitados_ids = [iid for iid in invitados_ids if iid not in invitados_invalidos]

                try:
                    invitacion = crear_invitacion(nombre, fecha, ubicacion_id)
                    if invitados_ids:
                        invitacion.invitados.set(invitados_ids)
                    if mesas_ids:
                        invitacion.mesas.set(mesas_ids)
                    messages.success(request, 'Invitación creada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al crear invitación: {str(e)}')
        
        # Crear mesa
        elif 'crear_mesa' in request.POST:
            nombre = request.POST.get('nombre_mesa', '').strip()
            if nombre:
                try:
                    crear_mesa(nombre)
                    messages.success(request, 'Mesa creada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al crear mesa: {str(e)}')
            else:
                messages.error(request, 'El nombre de la mesa es obligatorio')
        
        # Editar mesa
        elif 'editar_mesa' in request.POST:
            mesa_id = request.POST.get('mesa_id')
            nombre = request.POST.get('nombre_mesa', '').strip()
            if mesa_id and nombre:
                try:
                    actualizar_mesa(mesa_id, nombre)
                    messages.success(request, 'Mesa actualizada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al actualizar mesa: {str(e)}')
            else:
                messages.error(request, 'Todos los campos son obligatorios')
        
        # Eliminar mesa
        elif 'eliminar_mesa' in request.POST:
            mesa_id = request.POST.get('mesa_id')
            if mesa_id:
                try:
                    eliminar_mesa(mesa_id)
                    messages.success(request, 'Mesa eliminada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al eliminar mesa: {str(e)}')
            else:
                messages.error(request, 'ID de mesa no proporcionado')
        
        # Agregar ubicación
        elif 'agregar_ubicacion' in request.POST:
            nombre = request.POST.get('nombre_ubicacion', '').strip()
            direccion = request.POST.get('direccion_ubicacion', '').strip()
            google_maps_url = request.POST.get('google_maps_url', '').strip()
            if nombre and direccion and google_maps_url:
                try:
                    Ubicacion.objects.create(
                        nombre=nombre, 
                        direccion=direccion, 
                        google_maps_url=google_maps_url
                    )
                    messages.success(request, 'Ubicación agregada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al crear ubicación: {str(e)}')
            else:
                messages.error(request, 'Todos los campos de ubicación son obligatorios')
        
        # Setear fecha global
        elif 'setear_fecha_global' in request.POST:
            fecha = request.POST.get('fecha_global')
            if fecha:
                try:
                    fecha_evento.fecha = fecha
                    fecha_evento.save()
                    messages.success(request, 'Fecha global del evento actualizada')
                except Exception as e:
                    messages.error(request, f'Error al actualizar fecha: {str(e)}')
            else:
                messages.error(request, 'Debe ingresar una fecha válida')
        
        # Editar invitación
        elif 'editar_invitacion' in request.POST:
            invitacion_id = request.POST.get('invitacion_id')
            nombre = request.POST.get('nombre_invitacion', '').strip()
            invitados_ids = request.POST.getlist('invitados_invitacion')
            mesas_ids = request.POST.getlist('mesas_invitacion')

            invitacion_obj = None
            if invitacion_id:
                invitacion_obj = get_object_or_404(Invitacion, id=invitacion_id)

            if not invitacion_obj or not nombre:
                messages.error(request, 'ID de invitación y nombre son obligatorios.')
            else:
                # Fecha y ubicación permanecen globales (no editables desde este formulario)
                fecha = fecha_evento.fecha.isoformat() if fecha_evento and fecha_evento.fecha else None
                ubicacion_global = fecha_evento.ubicacion
                ubicacion_id = ubicacion_global.id if ubicacion_global else None

                # Validar invitados nuevos que no estén en otras invitaciones (excepto esta misma)
                invitados_invalidos = []
                for iid in invitados_ids:
                    if Invitacion.objects.filter(invitados__id=iid).exclude(id=invitacion_obj.id).exists():
                        invitados_invalidos.append(iid)

                if invitados_invalidos:
                    messages.error(request, 'Algunos invitados ya pertenecen a otra invitación y se omitieron.')
                    invitados_ids = [iid for iid in invitados_ids if iid not in invitados_invalidos]

                try:
                    invitacion_actualizada = actualizar_invitacion(invitacion_obj.id, nombre, fecha, ubicacion_id)
                    invitacion_actualizada.invitados.set(invitados_ids)
                    invitacion_actualizada.mesas.set(mesas_ids)
                    messages.success(request, 'Invitación actualizada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al actualizar invitación: {str(e)}')
        
        # Eliminar invitación
        elif 'eliminar_invitacion' in request.POST:
            invitacion_id = request.POST.get('invitacion_id')
            if invitacion_id:
                try:
                    eliminar_invitacion(invitacion_id)
                    messages.success(request, 'Invitación eliminada correctamente')
                except Exception as e:
                    messages.error(request, f'Error al eliminar invitación: {str(e)}')
            else:
                messages.error(request, 'ID de invitación no proporcionado')
    
    # Obtener datos para el template
    invitaciones = obtener_invitaciones()
    ubicaciones = Ubicacion.objects.all()
    mesas = obtener_mesas()
    invitados = obtener_invitados()
    confirmadas = [inv for inv in invitaciones if inv.confirmada]
    invitados_ocupados_ids = list(Invitacion.objects.values_list('invitados__id', flat=True).distinct())
    
    return render(request, 'invitaciones.html', {
        'invitaciones': invitaciones,
        'ubicaciones': ubicaciones,
        'mesas': mesas,
        'invitados': invitados,
        'fecha_evento': fecha_evento,
        'confirmadas': confirmadas,
        'invitados_ocupados_ids': invitados_ocupados_ids,
    })

def agregar_invitado(request):
    user_id = request.session.get('user_admin_id')
    if not user_id:
        return redirect('login')
    
    if request.method == 'POST':
        # Crear invitado
        if 'crear_invitado' in request.POST:
            nombre = request.POST.get('nombre_invitado', '').strip()
            apellido = request.POST.get('apellido_invitado', '').strip() or None
            if nombre:
                try:
                    crear_invitado(nombre, apellido)
                    messages.success(request, 'Invitado creado correctamente')
                except Exception as e:
                    messages.error(request, f'Error al crear invitado: {str(e)}')
            else:
                messages.error(request, 'El nombre es obligatorio para el invitado')
        
        # Editar invitado
        elif 'editar_invitado' in request.POST:
            invitado_id = request.POST.get('invitado_id')
            nombre = request.POST.get('nombre_invitado', '').strip()
            apellido = request.POST.get('apellido_invitado', '').strip() or None
            if invitado_id and nombre:
                try:
                    actualizar_invitado(invitado_id, nombre, apellido)
                    messages.success(request, 'Invitado actualizado correctamente')
                except Exception as e:
                    messages.error(request, f'Error al actualizar invitado: {str(e)}')
            else:
                messages.error(request, 'El nombre es obligatorio')
        
        # Eliminar invitado
        elif 'eliminar_invitado' in request.POST:
            invitado_id = request.POST.get('invitado_id')
            if invitado_id:
                try:
                    eliminar_invitado(invitado_id)
                    messages.success(request, 'Invitado eliminado correctamente')
                except Exception as e:
                    messages.error(request, f'Error al eliminar invitado: {str(e)}')
            else:
                messages.error(request, 'ID de invitado no proporcionado')
    
    invitados = obtener_invitados()
    return render(request, 'agregar_invitado.html', {
        'invitados': invitados,
    })

def logout(request):
    request.session.flush()  # Eliminar todas las sesiones
    return redirect('login')

def export_confirmed_guests(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="confirmed_guests_and_songs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Apellido', 'Canción', 'Artista'])

    # Fetch confirmed guests and their suggested songs
    confirmed_guests = Invitado.objects.filter(confirmado=True)
    for guest in confirmed_guests:
        playlists = Playlist.objects.filter(invitacion__invitados=guest)
        for playlist in playlists:
            writer.writerow([guest.nombre, guest.apellido, playlist.song_name, playlist.artist_name])

    return response