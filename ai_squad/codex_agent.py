# ai_squad/codex_agent.py
from __future__ import annotations
import json
from openai import OpenAI
from django.conf import settings


class CodexAgent:
    """Agente que usa OpenAI para generar código Django."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"  # Más económico y rápido
    
    def generate_backend_code(self, requirement: str, context: dict) -> dict:
        """
        Genera código backend basado en el requerimiento y contexto del proyecto.
        
        Args:
            requirement: Descripción de lo que se necesita implementar
            context: Contexto del proyecto (modelos, views, etc.)
        
        Returns:
            dict con files, commands, y metadata
        """
        prompt = self._build_prompt(requirement, context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Más determinístico
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "ok": True,
                "files": result.get("files", []),
                "commands": result.get("commands", []),
                "explanation": result.get("explanation", ""),
                "tests": result.get("tests", []),
                "tokens_used": response.usage.total_tokens,
                "model": self.model
            }
            
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "files": [],
                "commands": []
            }
    
    def _get_system_prompt(self) -> str:
        return """Eres un desarrollador senior de Django experto en:
- Django 4.2+ y Django REST Framework
- Arquitectura limpia y patrones de diseño
- Tests con pytest
- Buenas prácticas de seguridad

Tu tarea es generar código Django profesional basado en requerimientos.

IMPORTANTE:
- Genera SOLO el código necesario (mínimo viable)
- Incluye imports completos
- Sigue convenciones Django (PEP 8)
- Genera tests básicos
- Responde SIEMPRE en formato JSON válido

Formato de respuesta JSON:
{
  "explanation": "Breve explicación de los cambios",
  "files": [
    {
      "path": "ruta/relativa/archivo.py",
      "action": "create|modify",
      "content": "código completo del archivo",
      "description": "qué hace este archivo"
    }
  ],
  "commands": [
    "python manage.py makemigrations",
    "python manage.py migrate"
  ],
  "tests": [
    {
      "path": "tests/test_feature.py",
      "content": "código de tests"
    }
  ]
}"""
    
    def _build_prompt(self, requirement: str, context: dict) -> str:
        """Construye el prompt con el requerimiento y contexto."""
        
        prompt_parts = [
            "# REQUERIMIENTO",
            requirement,
            "",
            "# CONTEXTO DEL PROYECTO",
            f"Proyecto: Django {context.get('django_version', '4.2')}",
            f"Apps existentes: {', '.join(context.get('apps', []))}",
            "",
        ]
        
        # Agregar modelos existentes si hay
        if context.get('models'):
            prompt_parts.append("## Modelos existentes:")
            for model_info in context.get('models', [])[:5]:  # Limitar a 5
                prompt_parts.append(f"- {model_info}")
            prompt_parts.append("")
        
        # Agregar estructura de URLs si hay
        if context.get('urls'):
            prompt_parts.append("## URLs existentes:")
            for url in context.get('urls', [])[:10]:  # Limitar a 10
                prompt_parts.append(f"- {url}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "# INSTRUCCIONES",
            "1. Genera el código mínimo necesario para cumplir el requerimiento",
            "2. Usa las apps existentes cuando sea posible",
            "3. Sigue las convenciones del proyecto",
            "4. Incluye migraciones si modificas modelos",
            "5. Genera tests básicos",
            "",
            "Responde en formato JSON según el schema definido."
        ])
        
        return "\n".join(prompt_parts)
