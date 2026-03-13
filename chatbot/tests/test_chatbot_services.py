from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from chatbot.forms_chatbot import ApiKeyForm, SendMessageForm
from chatbot.models import Conversation, Message
from chatbot.services_chatbot import (
    get_or_create_bubble_conversation,
    send_message_to_chatbot,
    validate_api_key_format,
)


class ChatbotFormsTests(TestCase):
    def test_send_message_form_normaliza_espacios(self):
        form = SendMessageForm({'message': '  hola chatbot  '})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['message'], 'hola chatbot')

    def test_api_key_form_trim(self):
        form = ApiKeyForm({'api_key': '  sk-test  '})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['api_key'], 'sk-test')


class ChatbotServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='chatbot-user', password='secret')

    def test_get_or_create_bubble_conversation_reutiliza_sesion(self):
        conversation = Conversation.objects.create(user=self.user, title='Chat previo', is_active=True)
        session = {'chatbot_bubble_conversation_id': conversation.id}

        reused = get_or_create_bubble_conversation(session, self.user, 'hola')

        self.assertEqual(reused.id, conversation.id)

    @patch('chatbot.services_chatbot.EnhancedChatbotService.generate_response')
    def test_send_message_to_chatbot_persiste_historial(self, mock_generate_response):
        mock_generate_response.return_value = {'content': 'respuesta', 'tokens_used': 12}
        session = {}

        response = send_message_to_chatbot(session, self.user, 'hola')

        self.assertEqual(response['content'], 'respuesta')
        conversation = Conversation.objects.get(id=session['chatbot_bubble_conversation_id'])
        self.assertEqual(Message.objects.filter(conversation=conversation).count(), 2)

    def test_validate_api_key_format(self):
        self.assertTrue(validate_api_key_format('sk-test'))
        self.assertFalse(validate_api_key_format('test'))
