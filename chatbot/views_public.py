import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .forms_chatbot import FeedbackForm, SendMessageForm
from .selectors_chatbot import (
    get_user_conversation_queryset,
    get_user_conversations,
)
from .services_chatbot import send_message_to_chatbot, submit_feedback_for_message


def _json_payload(request):
    try:
        return json.loads(request.body or '{}'), None
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'JSON inválido'}, status=400)


def _first_form_error(form, default_message):
    if form.errors:
        return next(iter(form.errors.values()))[0]
    return default_message


@login_required
def chat_interface(request):
    conversations = get_user_conversations(request.user)
    active_conversation = conversations.first() if conversations.exists() else None
    return render(request, 'chatbot/chat_interface.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
    })


@login_required
@csrf_exempt
def send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = SendMessageForm(payload)
    if not form.is_valid() or not form.cleaned_data['message']:
        return JsonResponse({'error': _first_form_error(form, 'Mensaje vacío')}, status=400)

    try:
        response_data = send_message_to_chatbot(
            request.session,
            request.user,
            form.cleaned_data['message'],
        )
        return JsonResponse({
            'success': True,
            'response': response_data['content'],
        })
    except Exception:
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor',
        }, status=500)


@login_required
def load_conversation(request, conversation_id):
    conversation = get_object_or_404(get_user_conversation_queryset(request.user), id=conversation_id)
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title,
        'messages': [
            {
                'id': message.id,
                'role': message.role,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
            }
            for message in conversation.messages.all()
        ],
    })


@login_required
def new_conversation(request):
    from .models import Conversation

    conversation = Conversation.objects.create(
        user=request.user,
        title='Nueva conversación',
    )
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title,
    })


@login_required
@csrf_exempt
def submit_feedback(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    payload, error_response = _json_payload(request)
    if error_response:
        return error_response

    form = FeedbackForm(payload)
    if not form.is_valid():
        return JsonResponse({'error': _first_form_error(form, 'Feedback inválido')}, status=400)

    try:
        submit_feedback_for_message(request.user, form.cleaned_data)
        return JsonResponse({'success': True})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)
