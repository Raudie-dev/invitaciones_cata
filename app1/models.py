from django.db import models
from django.utils.crypto import get_random_string

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=500)
    google_maps_url = models.URLField()

    def __str__(self):
        return self.nombre

class Invitado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)
    confirmado = models.BooleanField(default=False)  # Nuevo campo para confirmar asistencia

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()

class Mesa(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Invitacion(models.Model):
    nombre = models.CharField(max_length=200)
    fecha = models.DateField()
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.CASCADE)
    numero_mesa = models.CharField(max_length=20, blank=True, null=True)
    invitados = models.ManyToManyField('Invitado', related_name='invitaciones', blank=True)
    mesas = models.ManyToManyField('Mesa', related_name='invitaciones', blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=32)
    confirmada = models.BooleanField(default=False)  # Nuevo campo para confirmar invitación

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = get_random_string(12)
        super().save(*args, **kwargs)

    def get_url(self):
        from django.urls import reverse
        return reverse('app1:index', kwargs={'slug': self.slug})

    def __str__(self):
        return self.nombre

class FechaEvento(models.Model):
    fecha = models.DateField()
    ubicacion = models.ForeignKey(Ubicacion, null=True, blank=True, on_delete=models.SET_NULL, help_text="Ubicación global del evento (opcional)")

    def __str__(self):
        base = str(self.fecha)
        if self.ubicacion:
            return f"{base} - {self.ubicacion.nombre}"
        return base

class Playlist(models.Model):
    invitacion = models.ForeignKey('Invitacion', on_delete=models.CASCADE, related_name='playlists')
    song_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.song_name} by {self.artist_name if self.artist_name else 'Unknown'}"
