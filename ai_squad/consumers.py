from __future__ import annotations

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser


class SquadRunConsumer(AsyncJsonWebsocketConsumer):
    """
    WS: /ws/ai-squad/runs/<run_id>/
    Se une al grupo: ai_squad_run_<run_id>
    Recibe eventos emitidos por ai_squad/events.py
    """

    async def connect(self):
        user = self.scope.get("user", None)
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4401)  # Unauthorized
            return

        self.run_id = self.scope["url_route"]["kwargs"]["run_id"]
        self.group_name = f"ai_squad_run_{self.run_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # ack inicial
        await self.send_json(
            {
                "event": "WS_CONNECTED",
                "payload": {"run_id": int(self.run_id)},
            }
        )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def ai_squad_event(self, event):
        """
        Handler llamado por group_send con:
        { "type": "ai_squad.event", "event": "<EVENT>", "payload": {...} }
        """
        await self.send_json(
            {
                "event": event.get("event"),
                "payload": event.get("payload", {}),
            }
        )
