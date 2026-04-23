import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from system_modules.models import ModuleState
from system_modules.services import sync_module_catalog


class ChatbotModuleGuardsTests(TestCase):
    def setUp(self):
        sync_module_catalog()
        self.user = User.objects.create_user(
            username="chatbot-user",
            password="clave-segura-123",
            is_staff=True,
        )

    def test_chat_interface_returns_403_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.get(reverse("chatbot:chat_interface"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Chatbot", status_code=403)

    def test_send_message_returns_json_when_module_is_disabled(self):
        ModuleState.objects.filter(slug="chatbot").update(is_enabled=False)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("chatbot:send_message"),
            data=json.dumps({"message": "hola"}),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["code"], "module_inactive")
