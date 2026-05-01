"""API publica del modulo conversaciones para shells y otros modulos."""

import logging

from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.html import escape

from conversaciones.models import Conversacion, HistorialAlertaConversacion, Mensaje
from conversaciones.infrastructure.services.core import AsignadorAutomatico, NotificacionService

logger = logging.getLogger(__name__)


def get_ciudadano_conversaciones(*, user, ciudadano):
    return Conversacion.objects.filter(
        Q(dni_ciudadano=ciudadano.dni) | Q(ciudadano_usuario=user)
    ).order_by("-fecha_inicio")


def get_ciudadano_conversacion_or_404(*, user, ciudadano, pk):
    conversacion = get_object_or_404(
        Conversacion.objects.prefetch_related("mensajes"),
        pk=pk,
    )
    if conversacion.dni_ciudadano != ciudadano.dni and conversacion.ciudadano_usuario != user:
        raise Http404
    return conversacion


def get_ciudadano_conversaciones_recientes(*, user, ciudadano, limit=3):
    return get_ciudadano_conversaciones(user=user, ciudadano=ciudadano)[:limit]


def get_conversaciones_by_dni(*, dni, limit=None):
    queryset = Conversacion.objects.filter(dni_ciudadano=dni).order_by("-fecha_inicio")
    if limit is not None:
        return queryset[:limit]
    return queryset


def count_mensajes_no_leidos_ciudadano(*, dni):
    return Mensaje.objects.filter(
        conversacion__dni_ciudadano=dni,
        conversacion__estado__in=["pendiente", "activa"],
        remitente="ciudadano",
        leido=False,
    ).count()


def get_historial_alertas_operador(*, operador, limit=20):
    return HistorialAlertaConversacion.objects.filter(
        operador=operador,
    ).select_related("conversacion", "operador").order_by("-creado")[:limit]


def get_monitoring_stats(*, since):
    conversacion_stats = Conversacion.objects.aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(estado="activa")),
    )
    return {
        "total": conversacion_stats["total"],
        "active": conversacion_stats["active"],
        "messages_today": Mensaje.objects.filter(fecha_envio__gte=since).count(),
    }


def _notificar_grupo(nombre_grupo, payload):
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(nombre_grupo, payload)
    except Exception as exc:
        logger.warning("No se pudo enviar notificacion realtime de consultas portal: %s", exc)


@transaction.atomic
def crear_consulta_ciudadana(*, ciudadano, user, motivo):
    conversacion = Conversacion.objects.create(
        tipo="personal",
        dni_ciudadano=ciudadano.dni,
        sexo_ciudadano=getattr(ciudadano, "genero", None) or None,
        ciudadano_usuario=user,
        estado="activa",
        prioridad="normal",
    )

    mensaje = None
    if motivo:
        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente="ciudadano",
            contenido=escape(motivo),
        )

    try:
        AsignadorAutomatico.asignar_conversacion_automatica(conversacion)
        NotificacionService.notificar_nueva_conversacion(conversacion)
    except Exception as exc:
        logger.warning("No se pudo autoasignar/notificar la conversacion %s: %s", conversacion.id, exc)

    _notificar_grupo(
        "conversaciones_list",
        {
            "type": "nueva_conversacion",
            "conversacion_id": conversacion.id,
            "mensaje": f"Nueva conversacion #{conversacion.id} creada desde portal ciudadano",
        },
    )

    if mensaje:
        _notificar_grupo(
            f"conversacion_{conversacion.id}",
            {
                "type": "chat_message",
                "mensaje": {
                    "id": mensaje.id,
                    "contenido": mensaje.contenido,
                    "remitente": "ciudadano",
                    "fecha": mensaje.fecha_envio.strftime("%H:%M"),
                    "usuario": "Ciudadano",
                },
            },
        )
        _notificar_grupo(
            "conversaciones_list",
            {
                "type": "nuevo_mensaje",
                "conversacion_id": conversacion.id,
                "mensaje": f"Nuevo mensaje en conversacion #{conversacion.id}",
            },
        )

    return conversacion


def crear_mensaje_ciudadano_desde_portal(*, conversacion, texto):
    if conversacion.estado == "cerrada":
        return None

    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        remitente="ciudadano",
        contenido=escape(texto),
    )

    _notificar_grupo(
        f"conversacion_{conversacion.id}",
        {
            "type": "chat_message",
            "mensaje": {
                "id": mensaje.id,
                "contenido": mensaje.contenido,
                "remitente": "ciudadano",
                "fecha": mensaje.fecha_envio.strftime("%H:%M"),
                "usuario": "Ciudadano",
            },
        },
    )
    _notificar_grupo(
        "conversaciones_list",
        {
            "type": "nuevo_mensaje",
            "conversacion_id": conversacion.id,
            "mensaje": f"Nuevo mensaje en conversacion #{conversacion.id}",
        },
    )

    return mensaje
