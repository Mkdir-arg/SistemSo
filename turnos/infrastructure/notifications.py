import logging

from django.core.mail import send_mail
from django.template.loader import render_to_string

from system_modules.guards import run_if_module_active

logger = logging.getLogger(__name__)


def send_confirmation(turno):
    return run_if_module_active("turnos", _send_confirmation, turno)


def send_cancellation(turno, motivo=""):
    return run_if_module_active("turnos", _send_cancellation, turno, motivo=motivo)


def _send_confirmation(turno):
    ciudadano = turno.ciudadano
    email = getattr(ciudadano, "email", "") or ""

    if not email:
        logger.warning(
            "Turno %s: ciudadano %s sin email - confirmacion no enviada.",
            turno.codigo_turno,
            ciudadano,
        )
        return

    nombre_entidad = turno.nombre_entidad
    try:
        cuerpo = render_to_string(
            "turnos/emails/turno_confirmado.html",
            {
                "turno": turno,
                "ciudadano": ciudadano,
                "nombre_entidad": nombre_entidad,
            },
        )
        send_mail(
            subject=f"Turno confirmado - {nombre_entidad}",
            message=(
                f"Tu turno {turno.codigo_turno} del "
                f'{turno.fecha.strftime("%d/%m/%Y")} a las '
                f'{turno.hora_inicio.strftime("%H:%M")} fue confirmado.'
            ),
            from_email=None,
            recipient_list=[email],
            html_message=cuerpo,
            fail_silently=False,
        )
        turno.email_confirmacion_enviado = True
        turno.save(update_fields=["email_confirmacion_enviado"])
        logger.info("Email de confirmacion enviado para turno %s a %s.", turno.codigo_turno, email)
    except Exception as exc:
        logger.error("Error enviando email de confirmacion para turno %s: %s", turno.codigo_turno, exc)


def _send_cancellation(turno, motivo=""):
    ciudadano = turno.ciudadano
    email = getattr(ciudadano, "email", "") or ""

    if not email:
        logger.warning(
            "Turno %s: ciudadano %s sin email - cancelacion no enviada.",
            turno.codigo_turno,
            ciudadano,
        )
        return

    nombre_entidad = turno.nombre_entidad
    try:
        cuerpo = render_to_string(
            "turnos/emails/turno_cancelado.html",
            {
                "turno": turno,
                "ciudadano": ciudadano,
                "nombre_entidad": nombre_entidad,
                "motivo": motivo,
            },
        )
        send_mail(
            subject=f"Turno cancelado - {nombre_entidad}",
            message=(
                f"Tu turno {turno.codigo_turno} del "
                f'{turno.fecha.strftime("%d/%m/%Y")} fue cancelado. '
                f"Motivo: {motivo}"
            ),
            from_email=None,
            recipient_list=[email],
            html_message=cuerpo,
            fail_silently=False,
        )
        turno.email_cancelacion_enviado = True
        turno.save(update_fields=["email_cancelacion_enviado"])
        logger.info("Email de cancelacion enviado para turno %s a %s.", turno.codigo_turno, email)
    except Exception as exc:
        logger.error("Error enviando email de cancelacion para turno %s: %s", turno.codigo_turno, exc)
