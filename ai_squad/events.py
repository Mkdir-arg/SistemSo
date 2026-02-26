# ai_squad/events.py
from __future__ import annotations

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def run_group_name(run_id: int) -> str:
    return f"ai_squad_run_{run_id}"


def emit_run_event(run_id: int, event: str, payload: dict) -> None:
    """
    Emite un evento a todos los clientes suscritos al grupo del run.
    Requiere un Consumer que se una al grupo: ai_squad_run_<id>
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        run_group_name(run_id),
        {
            "type": "ai_squad.event",   # handler en el consumer
            "event": event,
            "payload": payload,
        },
    )
