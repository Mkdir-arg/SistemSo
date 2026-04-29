import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie

from ..forms import (
    EvaluarConversacionForm,
    IniciarConversacionForm,
    MensajeConversacionForm,
    RenaperConsultaForm,
)
from ..models import Conversacion, FlujoPortalConversacion
from ..selectors import get_conversacion_detalle_queryset
from ..services.chat import (
    consultar_renaper_para_chat,
    crear_mensaje_ciudadano,
    evaluar_conversacion as evaluar_conversacion_service,
    iniciar_conversacion_publica,
)
from ..services.portal_bot import (
    enviar_mensaje_bot,
    iniciar_flujo_guiado,
    reactivar_flujo_post_login,
)

logger = logging.getLogger(__name__)


def _json_payload(request):
    try:
        return json.loads(request.body or '{}'), None
    except json.JSONDecodeError:
        return None, JsonResponse({'success': False, 'error': 'JSON inválido'})


def _first_form_error(form, default_message):
    if form.errors:
        return next(iter(form.errors.values()))[0]
    return default_message


@ensure_csrf_cookie
def chat_ciudadano(request):
    return render(request, 'conversaciones/chat_ciudadano.html')


def consultar_renaper(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = RenaperConsultaForm(payload)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'error': _first_form_error(form, 'DNI y sexo son requeridos'),
        })

    try:
        resultado = consultar_renaper_para_chat(
            form.cleaned_data['dni'],
            form.cleaned_data['sexo'],
        )
        if resultado['success']:
            datos = resultado['data']
            return JsonResponse({
                'success': True,
                'datos': {
                    'nombre': datos.get('nombre', ''),
                    'apellido': datos.get('apellido', ''),
                    'fecha_nacimiento': datos.get('fecha_nacimiento', ''),
                    'domicilio': datos.get('domicilio', ''),
                },
            })
        if resultado.get('fallecido'):
            return JsonResponse({
                'success': False,
                'error': 'La persona consultada figura como fallecida en RENAPER',
            })
        return JsonResponse({
            'success': False,
            'error': resultado.get('error', 'Error al consultar RENAPER'),
        })
    except Exception as exc:
        logger.error('Error en consulta RENAPER: %s', exc, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'})


def iniciar_conversacion(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = IniciarConversacionForm(payload)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'error': _first_form_error(form, 'Error al validar la conversación'),
        })

    try:
        conversacion = iniciar_conversacion_publica(form.cleaned_data, user=request.user)
        return JsonResponse({
            'success': True,
            'conversacion_id': conversacion.id,
        })
    except Exception as exc:
        logger.error('Error al crear conversación: %s', exc, exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Error al crear conversación: {str(exc)}',
        })


def enviar_mensaje_ciudadano(request, conversacion_id):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = MensajeConversacionForm(payload)
    if not form.is_valid():
        return JsonResponse({
            'success': False,
            'error': _first_form_error(form, 'Mensaje vacío'),
        })

    if not form.cleaned_data['mensaje']:
        return JsonResponse({'success': False, 'error': 'Mensaje vacío'})

    try:
        mensaje = crear_mensaje_ciudadano(conversacion_id, form.cleaned_data['mensaje'], user=request.user)
        return JsonResponse({
            'success': True,
            'mensaje': {
                'id': mensaje.id,
                'contenido': mensaje.contenido,
                'fecha': mensaje.fecha_envio.strftime('%H:%M'),
            },
        })
    except Exception as exc:
        logger.error('Error creando mensaje ciudadano: %s', exc, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'})


def obtener_mensajes_ciudadano(request, conversacion_id):
    conversacion = get_object_or_404(get_conversacion_detalle_queryset(), id=conversacion_id)
    mensajes = conversacion.mensajes.all()
    return JsonResponse({
        'mensajes': [
            {
                'id': msg.id,
                'remitente': msg.remitente,
                'contenido': msg.contenido,
                'fecha': msg.fecha_envio.strftime('%H:%M'),
            }
            for msg in mensajes
        ]
    })


def evaluar_conversacion(request, conversacion_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    evaluar_form = EvaluarConversacionForm({'satisfaccion': payload.get('satisfaccion')})
    if not evaluar_form.is_valid():
        return JsonResponse({
            'success': False,
            'error': _first_form_error(evaluar_form, 'Evaluación inválida'),
        })

    conversacion = get_object_or_404(Conversacion, id=conversacion_id)
    evaluar_conversacion_service(conversacion, evaluar_form.cleaned_data['satisfaccion'])
    return JsonResponse({'success': True})


def reactivar_bot_portal(request, conversacion_id):
    """Reactiva el flujo del bot al cargar la vista post-login.

    El JS del template llama a este endpoint al montar la página si el contexto
    indica que hay un flujo pendiente de reactivación.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    conversacion = get_object_or_404(
        Conversacion.objects.select_related('flujo_portal'),
        id=conversacion_id,
    )

    # Verificar propiedad de la conversación
    if conversacion.ciudadano_usuario_id != request.user.pk:
        return JsonResponse({'success': False, 'error': 'Sin acceso'}, status=403)

    texto_bot = reactivar_flujo_post_login(conversacion, user=request.user)
    if not texto_bot:
        return JsonResponse({'success': True, 'finalizado': True})

    mensaje = enviar_mensaje_bot(conversacion, texto_bot)
    return JsonResponse({
        'success': True,
        'mensaje': {
            'id': mensaje.id,
            'contenido': mensaje.contenido,
            'fecha': mensaje.fecha_envio.strftime('%H:%M'),
        },
    })


def iniciar_consulta_guiada(request):
    """Crea una nueva conversación con bot guiado desde el portal logueado.

    Recibe canal ('tramite_login' o 'reclamo_login') en el body JSON.
    Retorna el conversacion_id para que el JS redirija al detalle.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    canal = payload.get('canal', '')
    canales_validos = {
        FlujoPortalConversacion.Canal.TRAMITE_LOGIN,
        FlujoPortalConversacion.Canal.RECLAMO_LOGIN,
    }
    if canal not in canales_validos:
        return JsonResponse({'success': False, 'error': 'Canal inválido'})

    try:
        conversacion = iniciar_flujo_guiado(user=request.user, canal=canal)
        return JsonResponse({'success': True, 'conversacion_id': conversacion.id})
    except Exception as exc:
        logger.error('Error al iniciar consulta guiada: %s', exc, exc_info=True)
        return JsonResponse({'success': False, 'error': 'Error interno del servidor'})
