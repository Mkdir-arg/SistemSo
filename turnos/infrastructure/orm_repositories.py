"""Repositorios ORM y adaptadores de persistencia del modulo."""

from portal.models import DisponibilidadTurnos, TurnoCiudadano
from turnos.models import DisponibilidadConfiguracion


def count_occupied_slots(*, recurso, fecha, hora_inicio):
    return (
        TurnoCiudadano.objects.select_for_update()
        .filter(
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
            estado__in=["PENDIENTE", "CONFIRMADO"],
        )
        .count()
    )


def get_matching_disponibilidad(*, recurso, fecha, hora_inicio, hora_fin):
    disponibilidad = (
        DisponibilidadTurnos.objects.filter(
            recurso=recurso,
            dia_semana=fecha.weekday(),
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
            activo=True,
        )
        .first()
    )
    if disponibilidad:
        return disponibilidad
    if not getattr(recurso, "configuracion_turnos_id", None):
        return None
    return (
        DisponibilidadConfiguracion.objects.filter(
            configuracion_id=recurso.configuracion_turnos_id,
            dia_semana=fecha.weekday(),
            hora_inicio__lte=hora_inicio,
            hora_fin__gte=hora_fin,
            activo=True,
        )
        .first()
    )


def create_turno_ciudadano(**kwargs):
    return TurnoCiudadano.objects.create(**kwargs)


def get_turno_for_update(turno_id):
    return TurnoCiudadano.objects.select_for_update().get(pk=turno_id)


def save_turno(turno, update_fields=None):
    if update_fields:
        turno.save(update_fields=update_fields)
    else:
        turno.save()
    return turno
