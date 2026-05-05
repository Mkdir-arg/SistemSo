"""Helpers para ejecutar acciones automaticas del runtime de flujos."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from copy import deepcopy

import requests
from django.core.mail import send_mail
from django.utils import timezone


SUPPORTED_AUTOMATED_NODE_TYPES = frozenset({"accion_email", "accion_http"})
SUPPORTED_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})

_TEMPLATE_TOKEN_RE = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")
_FULL_TEMPLATE_TOKEN_RE = re.compile(r"^\s*\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}\s*$")


def merge_flow_context_data(current_data: dict | None, new_data: dict | None) -> dict:
    """Merge recursivo para preservar resultados previos en ramas anidadas."""
    merged = deepcopy(current_data or {})
    for key, value in (new_data or {}).items():
        if isinstance(merged.get(key), Mapping) and isinstance(value, Mapping):
            merged[key] = merge_flow_context_data(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def resolve_flow_context_path(data: Mapping | None, path: str):
    """Resuelve claves simples o paths con puntos sobre mappings anidados."""
    if not isinstance(data, Mapping) or not isinstance(path, str) or not path.strip():
        return None, False

    path = path.strip()
    if path in data:
        return data[path], True

    current = data
    for part in path.split('.'):
        if not isinstance(current, Mapping) or part not in current:
            return None, False
        current = current[part]
    return current, True


def build_flow_template_context(instancia) -> dict:
    """Contexto templateable disponible para pantallas y acciones."""
    data = deepcopy(instancia.datos or {})
    inscripcion = instancia.inscripcion
    programa = inscripcion.programa
    ciudadano = getattr(inscripcion, 'ciudadano', None)

    context = merge_flow_context_data(
        data,
        {
            'datos': data,
            'instancia': {
                'id': instancia.pk,
                'estado': instancia.estado,
                'nodo_actual': instancia.nodo_actual,
            },
            'inscripcion': {
                'id': inscripcion.pk,
                'estado': inscripcion.estado,
            },
            'programa': {
                'id': programa.pk,
                'codigo': programa.codigo,
                'nombre': programa.nombre,
            },
        },
    )

    if ciudadano is not None:
        context['ciudadano'] = {
            'id': ciudadano.pk,
            'dni': ciudadano.dni,
            'nombre': ciudadano.nombre,
            'apellido': ciudadano.apellido,
            'nombre_completo': ciudadano.nombre_completo,
            'email': ciudadano.email,
            'telefono': ciudadano.telefono,
        }

    return context


def render_flow_template_value(value, context):
    """Interpola strings con sintaxis {{ path.to.value }}."""
    if isinstance(value, str):
        full_match = _FULL_TEMPLATE_TOKEN_RE.match(value)
        if full_match:
            resolved, found = resolve_flow_context_path(context, full_match.group(1))
            if not found or resolved is None:
                return ''
            if isinstance(resolved, (dict, list)):
                return json.dumps(resolved, ensure_ascii=False)
            return str(resolved)

        def replace_token(match):
            resolved, found = resolve_flow_context_path(context, match.group(1))
            if not found or resolved is None:
                return ''
            if isinstance(resolved, (dict, list)):
                return json.dumps(resolved, ensure_ascii=False)
            return str(resolved)

        return _TEMPLATE_TOKEN_RE.sub(replace_token, value)

    if isinstance(value, list):
        return [render_flow_template_value(item, context) for item in value]

    if isinstance(value, Mapping):
        return {
            key: render_flow_template_value(item, context)
            for key, item in value.items()
        }

    return deepcopy(value)


def execute_automatic_node(instancia, nodo: dict):
    """Ejecuta un nodo automatico y devuelve actualizaciones de contexto y log."""
    node_type = nodo.get('tipo')
    if node_type == 'accion_email':
        return _execute_email_action(instancia, nodo)
    if node_type == 'accion_http':
        return _execute_http_action(instancia, nodo)
    raise ValueError(f'Tipo de accion automatica no soportado: "{node_type}".')


def _execute_email_action(instancia, nodo: dict):
    config = nodo.get('config') or {}
    email_config = render_flow_template_value(config.get('email') or {}, build_flow_template_context(instancia))

    recipients = [recipient.strip() for recipient in email_config.get('to', []) if isinstance(recipient, str) and recipient.strip()]
    if not recipients:
        raise ValueError(f'El nodo "{nodo.get("id")}" no tiene destinatarios válidos para enviar el email.')

    subject = (email_config.get('subject') or '').strip()
    body = email_config.get('body') or ''
    if not subject:
        raise ValueError(f'El nodo "{nodo.get("id")}" debe definir un asunto para el email.')
    if not isinstance(body, str) or not body.strip():
        raise ValueError(f'El nodo "{nodo.get("id")}" debe definir un cuerpo no vacío para el email.')

    sent_at = timezone.now().isoformat()
    try:
        sent_count = send_mail(
            subject=subject,
            message=body,
            from_email=None,
            recipient_list=recipients,
            fail_silently=False,
        )
        result = {
            'type': 'accion_email',
            'ok': sent_count > 0,
            'to': recipients,
            'subject': subject,
            'sent_at': sent_at,
        }
        if sent_count <= 0:
            result['error'] = 'El backend de correo no confirmo envios.'
    except Exception as exc:
        result = {
            'type': 'accion_email',
            'ok': False,
            'to': recipients,
            'subject': subject,
            'sent_at': sent_at,
            'error': str(exc),
        }

    return {
        'acciones': {
            nodo['id']: result,
        }
    }, result


def _headers_list_to_dict(headers):
    headers_dict = {}
    for header in headers:
        key = header.get('key', '').strip()
        value = header.get('value', '')
        if key:
            headers_dict[key] = value
    return headers_dict


def _extract_http_response_payload(response):
    content_type = response.headers.get('Content-Type', '')
    payload = {
        'status_code': response.status_code,
        'ok': response.ok,
        'reason': response.reason,
        'content_type': content_type,
    }
    if 'application/json' in content_type.lower():
        try:
            payload['json'] = response.json()
        except ValueError:
            payload['body'] = response.text[:2000]
    else:
        payload['body'] = response.text[:2000]
    return payload


def _execute_http_action(instancia, nodo: dict):
    config = nodo.get('config') or {}
    http_config = render_flow_template_value(config.get('http') or {}, build_flow_template_context(instancia))

    method = (http_config.get('method') or 'POST').upper()
    url = (http_config.get('url') or '').strip()
    if method not in SUPPORTED_HTTP_METHODS:
        raise ValueError(f'El nodo "{nodo.get("id")}" usa un metodo HTTP no soportado: "{method}".')
    if not url:
        raise ValueError(f'El nodo "{nodo.get("id")}" debe definir una URL para la accion HTTP.')

    timeout_seconds = http_config.get('timeout_seconds', 10)
    if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
        raise ValueError(f'El nodo "{nodo.get("id")}" debe definir timeout_seconds como entero positivo.')

    headers = _headers_list_to_dict(http_config.get('headers') or [])
    body = http_config.get('body', '')
    request_kwargs = {
        'method': method,
        'url': url,
        'headers': headers,
        'timeout': timeout_seconds,
    }
    if method != 'GET' and isinstance(body, str) and body.strip():
        request_kwargs['data'] = body

    executed_at = timezone.now().isoformat()
    try:
        response = requests.request(**request_kwargs)
        response_payload = _extract_http_response_payload(response)
        result = {
            'type': 'accion_http',
            'ok': response.ok,
            'method': method,
            'url': url,
            'executed_at': executed_at,
            **response_payload,
        }
    except requests.RequestException as exc:
        result = {
            'type': 'accion_http',
            'ok': False,
            'method': method,
            'url': url,
            'executed_at': executed_at,
            'error': str(exc),
        }

    return {
        'acciones': {
            nodo['id']: result,
        }
    }, result