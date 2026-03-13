from django.test import SimpleTestCase
from django.urls import reverse


class UrlNamespacesTests(SimpleTestCase):
    def test_users_namespace_and_legacy_name_coexist(self):
        self.assertEqual(reverse('users:usuarios'), '/usuarios/')
        self.assertEqual(reverse('usuarios'), '/usuarios/')
        self.assertEqual(reverse('users:logout'), '/logout')
        self.assertEqual(reverse('logout'), '/logout')

    def test_core_namespace_and_legacy_name_coexist(self):
        self.assertEqual(reverse('core:inicio'), '/inicio/')
        self.assertEqual(reverse('inicio'), '/inicio/')

    def test_healthcheck_namespace_and_legacy_name_coexist(self):
        self.assertEqual(reverse('healthcheck:health_check'), '/health/')
        self.assertEqual(reverse('health_check'), '/health/')

    def test_chatbot_y_conversaciones_tienen_namespaces_estables(self):
        self.assertEqual(reverse('chatbot:send_message'), '/chatbot/api/send-message/')
        self.assertEqual(reverse('conversaciones:detalle', kwargs={'conversacion_id': 7}), '/conversaciones/7/')
