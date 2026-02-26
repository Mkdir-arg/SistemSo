# chatbot/ai_service_enhanced.py
from openai import OpenAI
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Q
from legajos.models import Ciudadano
from .models import ChatbotKnowledge
import json


class EnhancedChatbotService:
    """Chatbot con capacidad de consultar la BD en tiempo real usando Function Calling."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Más económico y con function calling
        self.max_tokens = 800
    
    def get_available_functions(self):
        """Define las funciones que la IA puede llamar."""
        return {
            "consultar_ciudadanos": self.consultar_ciudadanos,
            "consultar_usuarios": self.consultar_usuarios,
            "buscar_ciudadano": self.buscar_ciudadano,
            "estadisticas_generales": self.estadisticas_generales,
        }
    
    def get_function_definitions(self):
        """Define el schema de funciones para OpenAI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "consultar_ciudadanos",
                    "description": "Consulta información sobre ciudadanos registrados en el sistema. Puede filtrar por estado, programa, o contar totales.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filtro": {
                                "type": "string",
                                "enum": ["todos", "activos", "inactivos"],
                                "description": "Filtro de estado de los ciudadanos"
                            },
                            "limite": {
                                "type": "integer",
                                "description": "Número máximo de resultados a retornar",
                                "default": 10
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consultar_usuarios",
                    "description": "Consulta información sobre usuarios del sistema (personal, administradores).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "activos_solo": {
                                "type": "boolean",
                                "description": "Si es true, solo retorna usuarios activos",
                                "default": True
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "buscar_ciudadano",
                    "description": "Busca un ciudadano específico por DNI o nombre.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dni": {
                                "type": "string",
                                "description": "DNI del ciudadano a buscar"
                            },
                            "nombre": {
                                "type": "string",
                                "description": "Nombre o apellido del ciudadano a buscar"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "estadisticas_generales",
                    "description": "Obtiene estadísticas generales del sistema (totales, promedios, etc).",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        ]
    
    # === FUNCIONES QUE LA IA PUEDE LLAMAR ===
    
    def consultar_ciudadanos(self, filtro="todos", limite=10):
        """Consulta ciudadanos con filtros."""
        try:
            queryset = Ciudadano.objects.all()
            
            if filtro == "activos":
                queryset = queryset.filter(activo=True)
            elif filtro == "inactivos":
                queryset = queryset.filter(activo=False)
            
            total = queryset.count()
            ciudadanos = queryset[:limite].values('dni', 'nombre', 'apellido', 'activo')
            
            return {
                "total": total,
                "mostrando": len(ciudadanos),
                "ciudadanos": list(ciudadanos)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def consultar_usuarios(self, activos_solo=True):
        """Consulta usuarios del sistema."""
        try:
            queryset = User.objects.all()
            
            if activos_solo:
                queryset = queryset.filter(is_active=True)
            
            total = queryset.count()
            usuarios = queryset.values('username', 'first_name', 'last_name', 'is_staff', 'is_active')[:20]
            
            return {
                "total": total,
                "usuarios": list(usuarios)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def buscar_ciudadano(self, dni=None, nombre=None):
        """Busca un ciudadano específico."""
        try:
            queryset = Ciudadano.objects.all()
            
            if dni:
                queryset = queryset.filter(dni__icontains=dni)
            elif nombre:
                queryset = queryset.filter(
                    Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre)
                )
            
            ciudadanos = queryset.values('dni', 'nombre', 'apellido', 'activo', 'fecha_nacimiento')[:5]
            
            return {
                "encontrados": queryset.count(),
                "resultados": list(ciudadanos)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def estadisticas_generales(self):
        """Obtiene estadísticas del sistema."""
        try:
            return {
                "ciudadanos_total": Ciudadano.objects.count(),
                "ciudadanos_activos": Ciudadano.objects.filter(activo=True).count(),
                "usuarios_total": User.objects.count(),
                "usuarios_activos": User.objects.filter(is_active=True).count(),
                "usuarios_staff": User.objects.filter(is_staff=True).count(),
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_system_context(self):
        """Contexto del sistema para la IA."""
        return """
        Eres un asistente del Sistema SEDRONAR con acceso a la base de datos.
        
        REGLAS OBLIGATORIAS:
        1. SIEMPRE usa las funciones disponibles para obtener datos reales
        2. NUNCA digas "no puedo proporcionar" - en su lugar USA las funciones
        3. Cuando pregunten por ciudadanos: llama a consultar_ciudadanos() o buscar_ciudadano()
        4. Cuando pregunten estadísticas: llama a estadisticas_generales()
        5. El usuario ESTÁ AUTENTICADO y tiene permisos para ver esta información
        
        EJEMPLOS:
        - "Cuántos ciudadanos hay?" → Llama consultar_ciudadanos()
        - "Cómo se llama el ciudadano?" → Llama consultar_ciudadanos(limite=5)
        - "Mostrame los ciudadanos" → Llama consultar_ciudadanos()
        - "Busca a Juan" → Llama buscar_ciudadano(nombre="Juan")
        
        Muestra los datos que obtengas: nombre, DNI, estado, etc.
        """
    
    def generate_response(self, message, conversation_history=None):
        """Genera respuesta usando OpenAI con Function Calling."""
        try:
            messages = [
                {"role": "system", "content": self.get_system_context()}
            ]
            
            # Agregar historial (últimos 5 mensajes)
            if conversation_history:
                if hasattr(conversation_history, 'only'):
                    history_msgs = conversation_history.only('role', 'content')[-5:]
                else:
                    history_msgs = conversation_history[-5:]
                
                for msg in history_msgs:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Mensaje actual
            messages.append({"role": "user", "content": message})
            
            # Primera llamada a OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.get_function_definitions(),
                tool_choice="required",  # FORZAR que use funciones
                max_tokens=self.max_tokens,
                temperature=0.3  # Más determinista
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls
            
            # Si la IA quiere llamar funciones
            if tool_calls:
                messages.append(response_message)
                
                available_functions = self.get_available_functions()
                
                # Ejecutar cada función que la IA solicitó
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Llamar a la función
                    function_to_call = available_functions.get(function_name)
                    if function_to_call:
                        function_response = function_to_call(**function_args)
                        
                        # Agregar resultado al contexto
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(function_response, ensure_ascii=False)
                        })
                
                # Segunda llamada con los resultados de las funciones
                second_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=0.7
                )
                
                final_message = second_response.choices[0].message.content
                total_tokens = response.usage.total_tokens + second_response.usage.total_tokens
            else:
                # No necesitó llamar funciones
                final_message = response_message.content
                total_tokens = response.usage.total_tokens
            
            return {
                'content': final_message,
                'tokens_used': total_tokens,
                'used_functions': bool(tool_calls)
            }
            
        except Exception as e:
            return {
                'content': f"Error: {str(e)}",
                'tokens_used': 0,
                'error': str(e)
            }
