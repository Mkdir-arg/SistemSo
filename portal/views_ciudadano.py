from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from core.decorators import ciudadano_required
from legajos.models_programas import InscripcionPrograma, DerivacionPrograma
from .forms import (
    CiudadanoCambioEmailForm,
    CiudadanoCambioPasswordForm,
    CiudadanoEditarDatosForm,
)
from .views_ciudadano_auth import (
    CiudadanoLoginView,
    CiudadanoLogoutView,
    CiudadanoPasswordResetCompleteView,
    CiudadanoPasswordResetConfirmView,
    CiudadanoPasswordResetDoneView,
    CiudadanoPasswordResetView,
    RegistroStep1View,
    RegistroStep2View,
)
from .views_ciudadano_consultas import (
    ciudadano_consulta_detalle,
    ciudadano_enviar_mensaje,
    ciudadano_mis_consultas,
    ciudadano_nueva_consulta,
)
from .views_ciudadano_turnos import (
    ciudadano_cancelar_turno,
    ciudadano_confirmar_turno,
    ciudadano_mis_turnos,
    ciudadano_solicitar_turno,
    ciudadano_turno_calendario,
    ciudadano_turno_confirmado,
    ciudadano_turno_slots,
)


@ciudadano_required
def ciudadano_mi_perfil(request):
    from django.db.models import Q
    from conversaciones.models import Conversacion
    import datetime

    ciudadano = request.user.ciudadano_perfil

    # Inscripciones activas (related_name real: inscripciones_programas)
    inscripciones_activas = []
    if hasattr(ciudadano, 'inscripciones_programas'):
        inscripciones_activas = list(
            ciudadano.inscripciones_programas.filter(
                estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
            ).select_related('programa')[:5]
        )

    # Últimas 3 conversaciones del ciudadano
    conversaciones_recientes = Conversacion.objects.filter(
        Q(dni_ciudadano=ciudadano.dni) | Q(ciudadano_usuario=request.user)
    ).order_by('-fecha_inicio')[:3]

    # Timeline: últimos eventos (inscripciones + conversaciones, ordenados por fecha)
    eventos = []

    inscripciones_timeline = []
    if hasattr(ciudadano, 'inscripciones_programas'):
        inscripciones_timeline = ciudadano.inscripciones_programas.select_related('programa').order_by('-fecha_inscripcion')[:3]

    for insc in inscripciones_timeline:
        # fecha_inscripcion es DateField; convertir a datetime naive para ordenar con fecha_inicio de Conversacion
        fecha_dt = datetime.datetime.combine(insc.fecha_inscripcion, datetime.time.min)
        eventos.append({
            'tipo': 'programa',
            'icono': 'fa-clipboard-list',
            'color': 'blue',
            'descripcion': f'Inscripción al programa {insc.programa.nombre}',
            'fecha': fecha_dt,
            'fecha_display': insc.fecha_inscripcion,
            'estado': insc.estado,
        })

    for conv in Conversacion.objects.filter(
        Q(dni_ciudadano=ciudadano.dni) | Q(ciudadano_usuario=request.user)
    ).order_by('-fecha_inicio')[:3]:
        # Usar datetime naive para comparación homogénea con las fechas de inscripción
        fecha_naive = conv.fecha_inicio.replace(tzinfo=None) if conv.fecha_inicio.tzinfo else conv.fecha_inicio
        eventos.append({
            'tipo': 'consulta',
            'icono': 'fa-comments',
            'color': 'green',
            'descripcion': 'Consulta iniciada',
            'fecha': fecha_naive,
            'fecha_display': conv.fecha_inicio,
            'estado': conv.estado,
        })

    eventos.sort(key=lambda x: x['fecha'], reverse=True)
    eventos = eventos[:5]

    context = {
        'ciudadano': ciudadano,
        'inscripciones_activas': inscripciones_activas,
        'conversaciones_recientes': conversaciones_recientes,
        'eventos': eventos,
    }
    return render(request, 'portal/ciudadano/mi_perfil.html', context)


@ciudadano_required
def ciudadano_mis_programas(request):
    ciudadano = request.user.ciudadano_perfil

    inscripciones_activas = ciudadano.inscripciones_programas.filter(
        estado__in=['ACTIVO', 'EN_SEGUIMIENTO', 'PENDIENTE']
    ).select_related('programa').order_by('-fecha_inscripcion')

    inscripciones_historial = ciudadano.inscripciones_programas.filter(
        estado__in=['CERRADO', 'SUSPENDIDO']
    ).select_related('programa').order_by('-fecha_inscripcion')

    context = {
        'ciudadano': ciudadano,
        'inscripciones_activas': inscripciones_activas,
        'inscripciones_historial': inscripciones_historial,
    }
    return render(request, 'portal/ciudadano/mis_programas.html', context)


@ciudadano_required
def ciudadano_programa_detalle(request, pk):
    ciudadano = request.user.ciudadano_perfil

    # Anti-IDOR: get_object_or_404 filtra por pk Y por ciudadano autenticado
    inscripcion = get_object_or_404(
        InscripcionPrograma,
        pk=pk,
        ciudadano=ciudadano
    )

    # Derivaciones donde este ciudadano fue derivado al programa de esta inscripción
    derivaciones = DerivacionPrograma.objects.filter(
        ciudadano=ciudadano,
        programa_destino=inscripcion.programa
    ).select_related('programa_origen', 'programa_destino').order_by('-creado')

    context = {
        'ciudadano': ciudadano,
        'inscripcion': inscripcion,
        'derivaciones': derivaciones,
    }
    return render(request, 'portal/ciudadano/programa_detalle.html', context)


@ciudadano_required
def ciudadano_mis_datos(request):
    ciudadano = request.user.ciudadano_perfil

    if request.method == 'POST':
        form = CiudadanoEditarDatosForm(request.POST, instance=ciudadano)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tus datos fueron actualizados correctamente.')
            return redirect('portal:ciudadano_mis_datos')
    else:
        form = CiudadanoEditarDatosForm(instance=ciudadano)

    context = {
        'ciudadano': ciudadano,
        'form': form,
    }
    return render(request, 'portal/ciudadano/mis_datos.html', context)


@ciudadano_required
def ciudadano_cambio_email(request):
    ciudadano = request.user.ciudadano_perfil

    if request.method == 'POST':
        form = CiudadanoCambioEmailForm(request.POST)
        if form.is_valid():
            from users.models import SolicitudCambioEmail
            from django.core.mail import send_mail
            from django.urls import reverse

            nuevo_email = form.cleaned_data['nuevo_email']

            # Invalidar solicitudes previas pendientes
            SolicitudCambioEmail.objects.filter(
                user=request.user, confirmado=False, expirado=False
            ).update(expirado=True)

            solicitud = SolicitudCambioEmail.objects.create(
                user=request.user,
                nuevo_email=nuevo_email,
            )

            link = request.build_absolute_uri(
                reverse('portal:ciudadano_confirmar_email', kwargs={'token': str(solicitud.token)})
            )
            send_mail(
                subject='Confirmar cambio de email — Portal Ciudadano',
                message=(
                    f'Hacé clic en el siguiente enlace para confirmar tu nuevo email:\n\n'
                    f'{link}\n\n'
                    f'Este enlace vence en 24 horas.'
                ),
                from_email=None,
                recipient_list=[nuevo_email],
                fail_silently=False,
            )
            messages.success(request, f'Te enviamos un email a {nuevo_email} para confirmar el cambio.')
            return redirect('portal:ciudadano_mis_datos')
    else:
        form = CiudadanoCambioEmailForm()

    context = {
        'ciudadano': ciudadano,
        'form': form,
    }
    return render(request, 'portal/ciudadano/cambio_email.html', context)


def ciudadano_confirmar_email(request, token):
    """Vista pública — el link llega por email, no requiere sesión activa."""
    from users.models import SolicitudCambioEmail

    solicitud = get_object_or_404(SolicitudCambioEmail, token=token, confirmado=False, expirado=False)

    if not solicitud.esta_vigente:
        messages.error(request, 'Este enlace expiró. Solicitá un nuevo cambio de email.')
        return redirect('portal:ciudadano_login')

    user = solicitud.user
    ciudadano = user.ciudadano_perfil

    user.email = solicitud.nuevo_email
    user.save()

    ciudadano.email = solicitud.nuevo_email
    ciudadano.save()

    solicitud.confirmado = True
    solicitud.save()

    messages.success(request, 'Tu email fue actualizado correctamente.')
    return redirect('portal:ciudadano_mis_datos')


@ciudadano_required
def ciudadano_cambio_password(request):
    from django.contrib.auth import update_session_auth_hash

    ciudadano = request.user.ciudadano_perfil

    if request.method == 'POST':
        form = CiudadanoCambioPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña fue cambiada correctamente.')
            return redirect('portal:ciudadano_mis_datos')
    else:
        form = CiudadanoCambioPasswordForm(request.user)

    context = {
        'ciudadano': ciudadano,
        'form': form,
    }
    return render(request, 'portal/ciudadano/cambio_password.html', context)


# ─── Sistema de Turnos ────────────────────────────────────────────────────────
