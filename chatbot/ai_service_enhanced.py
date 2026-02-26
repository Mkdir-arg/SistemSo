from openai import OpenAI
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from legajos.models import Ciudadano
from .models import ChatbotKnowledge
import json


class EnhancedChatbotService:
    """Chatbot con capacidad de consultar la BD en tiempo real."""
    
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-3.5-turbo"
            self.max_tokens = 500
            self.openai_available = True
        else:
            self.client = None
            self.openai_available = False
    
    def consultar_ciudadanos(self):
        """Consulta ciudadanos."""
        try:
            total = Ciudadano.objects.count()
            activos = Ciudadano.objects.filter(activo=True).count()
            return f"Total: {total} ciudadanos ({activos} activos)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def consultar_usuarios(self):
        """Consulta usuarios."""
        try:
            total = User.objects.count()
            activos = User.objects.filter(is_active=True).count()
            return f"Total: {total} usuarios ({activos} activos)"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_system_context(self):
        """Contexto del sistema."""
        stats = f"""
Estadísticas del sistema:
- {self.consultar_ciudadanos()}
- {self.consultar_usuarios()}
"""
        return f"""
Eres un asistente del Sistema SEDRONAR.

{stats}

Responde de forma amigable y profesional.
"""
    
    def generate_response(self, message, conversation_history=None):
        """Genera respuesta."""
        try:
            # Respuestas rápidas
            msg_lower = message.lower().strip()
            
            if any(s in msg_lower for s in ['hola', 'buenos dias', 'buenas tardes', 'hey']):
                return {
                    'content': '¡Hola! Soy el Asistente NODO. Pregúntame sobre ciudadanos, usuarios o estadísticas del sistema.',
                    'tokens_used': 0
                }
            
            if 'cuantos ciudadanos' in msg_lower or 'cuántos ciudadanos' in msg_lower:
                return {
                    'content': self.consultar_ciudadanos(),
                    'tokens_used': 0
                }
            
            if 'cuantos usuarios' in msg_lower or 'cuántos usuarios' in msg_lower:
                return {
                    'content': self.consultar_usuarios(),
                    'tokens_used': 0
                }
            
            # Si no hay OpenAI
            if not self.openai_available:
                return {
                    'content': 'Puedo ayudarte con: ¿Cuántos ciudadanos hay? ¿Cuántos usuarios hay?',
                    'tokens_used': 0
                }
            
            # Usar OpenAI
            messages = [
                {"role": "system", "content": self.get_system_context()},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                'content': '¡Hola! Soy el Asistente NODO. Pregúntame sobre ciudadanos o usuarios del sistema.',
                'tokens_used': 0,
                'error': str(e)
            }
