"""API publica del modulo conversaciones para shells y otros modulos."""

import logging

from django.db import transaction
from django.utils.html import escape

from conversaciones.models import Conversacion, Mensaje
from conversaciones.services.core import AsignadorAutomatico, NotificacionService

logger = logging.getLogger(__name__)


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
