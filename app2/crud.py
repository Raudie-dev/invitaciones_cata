from app1.models import Invitacion, Ubicacion, Mesa, Invitado
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404

# Invitacion CRUD
def crear_invitacion(nombre, fecha, ubicacion_id):
    try:
        ubicacion = Ubicacion.objects.get(id=ubicacion_id)
        slug = get_random_string(12)
        # Verificar que el slug sea único
        while Invitacion.objects.filter(slug=slug).exists():
            slug = get_random_string(12)
        return Invitacion.objects.create(nombre=nombre, fecha=fecha, ubicacion=ubicacion, slug=slug)
    except Ubicacion.DoesNotExist:
        raise ValueError("La ubicación no existe")
    except Exception as e:
        raise ValueError(f"Error al crear invitación: {str(e)}")

def obtener_invitaciones():
    return Invitacion.objects.select_related('ubicacion').prefetch_related('invitados', 'mesas').all()

def eliminar_invitacion(invitacion_id):
    try:
        invitacion = get_object_or_404(Invitacion, id=invitacion_id)
        invitacion.delete()
        return True
    except Invitacion.DoesNotExist:
        raise ValueError("La invitación no existe")
    except Exception as e:
        raise ValueError(f"Error al eliminar invitación: {str(e)}")

def actualizar_invitacion(invitacion_id, nombre=None, fecha=None, ubicacion_id=None):
    try:
        invitacion = get_object_or_404(Invitacion, id=invitacion_id)
        if nombre is not None:
            invitacion.nombre = nombre
        if fecha is not None:
            invitacion.fecha = fecha
        if ubicacion_id is not None:
            ubicacion = get_object_or_404(Ubicacion, id=ubicacion_id)
            invitacion.ubicacion = ubicacion
        invitacion.save()
        return invitacion
    except Exception as e:
        raise ValueError(f"Error al actualizar invitación: {str(e)}")

# Mesa CRUD
def crear_mesa(nombre):
    try:
        if not nombre or nombre.strip() == '':
            raise ValueError("El nombre de la mesa no puede estar vacío")
        return Mesa.objects.create(nombre=nombre.strip())
    except Exception as e:
        raise ValueError(f"Error al crear mesa: {str(e)}")

def obtener_mesas():
    return Mesa.objects.all().order_by('nombre')

def eliminar_mesa(mesa_id):
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        mesa.delete()
        return True
    except Mesa.DoesNotExist:
        raise ValueError("La mesa no existe")
    except Exception as e:
        raise ValueError(f"Error al eliminar mesa: {str(e)}")

def actualizar_mesa(mesa_id, nombre):
    try:
        mesa = get_object_or_404(Mesa, id=mesa_id)
        if not nombre or nombre.strip() == '':
            raise ValueError("El nombre de la mesa no puede estar vacío")
        mesa.nombre = nombre.strip()
        mesa.save()
        return mesa
    except Exception as e:
        raise ValueError(f"Error al actualizar mesa: {str(e)}")

# Invitado CRUD
def crear_invitado(nombre, apellido=None):
    try:
        if not nombre or nombre.strip() == '':
            raise ValueError("El nombre del invitado no puede estar vacío")
        
        nombre = nombre.strip()
        if apellido:
            apellido = apellido.strip()
            
        return Invitado.objects.create(nombre=nombre, apellido=apellido)
    except Exception as e:
        raise ValueError(f"Error al crear invitado: {str(e)}")

def obtener_invitados():
    return Invitado.objects.all().order_by('nombre', 'apellido')

def eliminar_invitado(invitado_id):
    try:
        invitado = get_object_or_404(Invitado, id=invitado_id)
        invitado.delete()
        return True
    except Invitado.DoesNotExist:
        raise ValueError("El invitado no existe")
    except Exception as e:
        raise ValueError(f"Error al eliminar invitado: {str(e)}")

def actualizar_invitado(invitado_id, nombre, apellido=None):
    try:
        invitado = get_object_or_404(Invitado, id=invitado_id)
        if not nombre or nombre.strip() == '':
            raise ValueError("El nombre del invitado no puede estar vacío")
        
        invitado.nombre = nombre.strip()
        if apellido:
            invitado.apellido = apellido.strip()
        else:
            invitado.apellido = None
            
        invitado.save()
        return invitado
    except Exception as e:
        raise ValueError(f"Error al actualizar invitado: {str(e)}")