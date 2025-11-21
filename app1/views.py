from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Invitacion, Playlist
from django.contrib import messages


# Create your views here.
def index(request, slug):
    invitacion = get_object_or_404(Invitacion.objects.prefetch_related('invitados', 'mesas'), slug=slug)

    if request.method == 'POST':
        # Confirmar asistencia de la invitación
        invitacion.confirmada = True
        invitacion.save()

        # Confirmar asistencia de los invitados relacionados
        invitacion.invitados.update(confirmado=True)

        # Guardar sugerencia de canción
        song_names = request.POST.getlist('song_name[]')
        artist_names = request.POST.getlist('artist_name[]')
        for song_name, artist_name in zip(song_names, artist_names):
            if song_name.strip():
                Playlist.objects.create(
                    invitacion=invitacion,
                    song_name=song_name.strip(),
                    artist_name=artist_name.strip() if artist_name else None
                )

        messages.success(request, 'Asistencia confirmada exitosamente, incluyendo los invitados relacionados.')
        # Flag en sesión para desplegar overlay animado tras la redirección (PRG pattern)
        request.session['confirm_success'] = True
        return HttpResponseRedirect(request.path_info)

    # Recuperar flag de confirmación y eliminarla para no repetir
    confirm_success = False
    if request.session.get('confirm_success'):
        confirm_success = True
        del request.session['confirm_success']

    return render(request, 'index.html', {
        'invitacion': invitacion,
        'confirm_success': confirm_success,
    })
