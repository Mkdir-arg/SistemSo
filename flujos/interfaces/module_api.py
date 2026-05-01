"""Contrato publico estable del modulo."""

from django.utils import timezone


def iniciar_flujo_inscripcion(inscripcion):
    from flujos.runtime import FlowRuntime

    return FlowRuntime.iniciar(inscripcion)


def cancelar_instancia_inscripcion(*, inscripcion, usuario, motivo):
    try:
        instancia = inscripcion.instancia_flujo
    except Exception:
        return None

    if instancia.estado != "ACTIVA":
        return instancia

    from flujos.models import InstanciaLog

    instancia.estado = "CANCELADA"
    instancia.fecha_cierre = timezone.now()
    instancia.save(update_fields=["estado", "fecha_cierre"])
    InstanciaLog.objects.create(
        instancia=instancia,
        nodo_desde=instancia.nodo_actual,
        nodo_hasta="BAJA",
        usuario=usuario,
        motivo=f"Baja del programa: {motivo}",
    )
    return instancia
