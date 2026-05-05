"""Casos de uso orquestados del modulo."""

from django.db import transaction

from flujos.models import InstanciaLog, TareaFlujo
from flujos.runtime import FlowRuntime


class FlowTaskActionError(ValueError):
    """Error controlado al operar tareas del runtime."""


@transaction.atomic
def asignar_tarea_flujo(*, tarea: TareaFlujo, usuario_asignado, usuario_actor=None):
    if tarea.estado != TareaFlujo.Estado.PENDIENTE:
        raise FlowTaskActionError('Solo se pueden asignar tareas pendientes.')

    asignado_anterior = tarea.asignado_a
    if asignado_anterior == usuario_asignado:
        return tarea

    tarea.asignado_a = usuario_asignado
    tarea.save(update_fields=['asignado_a'])

    if asignado_anterior is None and usuario_asignado is None:
        return tarea

    if asignado_anterior is None:
        motivo = 'Asignacion de tarea'
    elif usuario_asignado is None:
        motivo = 'Desasignacion de tarea'
    else:
        motivo = 'Reasignacion de tarea'

    InstanciaLog.objects.create(
        instancia=tarea.instancia,
        nodo_desde=tarea.nodo_id,
        nodo_hasta=tarea.nodo_id,
        usuario=usuario_actor,
        motivo=motivo,
        datos_transicion={
            'evento': 'asignacion_tarea',
            'tarea_id': tarea.pk,
            'nodo_id': tarea.nodo_id,
            'asignado_anterior_id': asignado_anterior.pk if asignado_anterior else None,
            'asignado_nuevo_id': usuario_asignado.pk if usuario_asignado else None,
            'asignado_anterior_username': (
                asignado_anterior.username if asignado_anterior else None
            ),
            'asignado_nuevo_username': (
                usuario_asignado.username if usuario_asignado else None
            ),
        },
    )
    return tarea


def resolver_tarea_flujo(*, tarea: TareaFlujo, usuario, datos=None):
    if tarea.estado != TareaFlujo.Estado.PENDIENTE:
        raise FlowTaskActionError('La tarea ya fue procesada.')

    instancia = tarea.instancia
    if instancia.estado != instancia.Estado.ACTIVA:
        raise FlowTaskActionError('La instancia de flujo ya no está activa.')

    if instancia.nodo_actual != tarea.nodo_id:
        raise FlowTaskActionError('La tarea no coincide con el nodo actual de la instancia.')

    try:
        return FlowRuntime.avanzar(instancia, datos=datos or {}, usuario=usuario)
    except ValueError as exc:
        raise FlowTaskActionError(str(exc)) from exc
