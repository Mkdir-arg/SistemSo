from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View

from core.decorators import ciudadano_required
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, DerivacionPrograma
from legajos.services.consulta_renaper import consultar_datos_renaper
from .forms import (
    CiudadanoLoginForm,
    CiudadanoCambioEmailForm,
    CiudadanoCambioPasswordForm,
    CiudadanoEditarDatosForm,
    CiudadanoPasswordResetForm,
    RegistroStep1Form,
    RegistroStep2Form,
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

LOGIN_MAX_INTENTOS = 5
LOGIN_BLOQUEO_SEGUNDOS = 300  # 5 minutos


def _cache_key_login(ip):
    return f'login_intentos_{ip}'


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class CiudadanoLoginView(View):
    template_name = 'portal/ciudadano/login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.groups.filter(name='Ciudadanos').exists():
            return redirect('portal:ciudadano_mi_perfil')
        form = CiudadanoLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        ip = _get_client_ip(request)
        cache_key = _cache_key_login(ip)
        intentos = cache.get(cache_key, 0)

        if intentos >= LOGIN_MAX_INTENTOS:
            messages.error(request, 'Demasiados intentos fallidos. Intentá de nuevo en 5 minutos.')
            return render(request, self.template_name, {'form': CiudadanoLoginForm(), 'bloqueado': True})

        form = CiudadanoLoginForm(request, data=request.POST)
        if form.is_valid():
            cache.delete(cache_key)
            login(request, form.get_user())
            return redirect('portal:ciudadano_mi_perfil')

        # Incrementar contador de intentos fallidos
        cache.set(cache_key, intentos + 1, LOGIN_BLOQUEO_SEGUNDOS)
        return render(request, self.template_name, {'form': form})


class CiudadanoLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('portal:ciudadano_login')


class RegistroStep1View(View):
    template_name = 'portal/ciudadano/registro_step1.html'

    def get(self, request):
        form = RegistroStep1Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegistroStep1Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        dni = form.cleaned_data['dni']
        genero = form.cleaned_data['genero']

        # Verificar si el DNI ya tiene usuario registrado
        try:
            ciudadano = Ciudadano.objects.get(dni=dni)
            if ciudadano.usuario_id:
                # Flujo 3: ya tiene cuenta
                messages.info(request, 'Ya tenés una cuenta registrada. Iniciá sesión con tu DNI y contraseña.')
                return redirect('portal:ciudadano_login')
            else:
                # Flujo 2: tiene legajo pero sin usuario
                # No se guarda nombre/apellido para evitar exposición de datos del legajo
                request.session['registro_ciudadano'] = {
                    'flujo': 'legajo_existente',
                    'ciudadano_id': ciudadano.pk,
                    'dni': dni,
                }
                return redirect('portal:ciudadano_registro_step2')
        except Ciudadano.DoesNotExist:
            pass

        # Flujo 1: ciudadano nuevo — consultar RENAPER
        try:
            resultado = consultar_datos_renaper(dni, genero)
            if not resultado.get('success'):
                form.add_error('dni', 'No pudimos verificar tu identidad. Verificá los datos ingresados.')
                return render(request, self.template_name, {'form': form})
            datos_renaper = resultado['data']
        except Exception:
            form.add_error(None, 'El servicio de verificación no está disponible. Intentá más tarde.')
            return render(request, self.template_name, {'form': form})

        request.session['registro_ciudadano'] = {
            'flujo': 'nuevo',
            'dni': dni,
            'genero': genero,
            'nombre': datos_renaper.get('nombre', ''),
            'apellido': datos_renaper.get('apellido', ''),
        }
        return redirect('portal:ciudadano_registro_step2')


class RegistroStep2View(View):
    template_name = 'portal/ciudadano/registro_step2.html'

    def get(self, request):
        datos = request.session.get('registro_ciudadano')
        if not datos:
            return redirect('portal:ciudadano_registro_step1')
        form = RegistroStep2Form()
        return render(request, self.template_name, {'form': form, 'datos': datos})

    def post(self, request):
        datos = request.session.get('registro_ciudadano')
        if not datos:
            return redirect('portal:ciudadano_registro_step1')

        form = RegistroStep2Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'datos': datos})

        dni = datos['dni']
        email = form.cleaned_data['email']
        telefono = form.cleaned_data['telefono']
        password = form.cleaned_data['password1']

        # Verificar que el DNI no tenga ya un User (doble check por race condition)
        if User.objects.filter(username=dni).exists():
            messages.error(request, 'Ya existe una cuenta con ese DNI.')
            return redirect('portal:ciudadano_login')

        # Crear el User
        user = User.objects.create_user(username=dni, email=email, password=password)
        grupo = Group.objects.get(name='Ciudadanos')
        user.groups.add(grupo)

        flujo = datos.get('flujo')
        if flujo == 'legajo_existente':
            ciudadano = get_object_or_404(Ciudadano, pk=datos['ciudadano_id'])

            # Re-verificar race condition: otro proceso pudo haber asignado usuario entre Step1 y Step2
            if ciudadano.usuario_id:
                user.delete()
                messages.error(request, 'Este legajo ya tiene una cuenta asociada. Iniciá sesión.')
                del request.session['registro_ciudadano']
                return redirect('portal:ciudadano_login')

            ciudadano.usuario = user
            if email:
                ciudadano.email = email
            if telefono:
                ciudadano.telefono = telefono
            ciudadano.save()
        else:
            # Flujo nuevo: crear el Ciudadano
            ciudadano = Ciudadano.objects.create(
                dni=dni,
                nombre=datos.get('nombre', ''),
                apellido=datos.get('apellido', ''),
                email=email,
                telefono=telefono or '',
                genero=datos.get('genero', 'X'),
                usuario=user,
            )

        user.first_name = ciudadano.nombre
        user.last_name = ciudadano.apellido
        user.save()

        # Limpiar sesión de registro
        del request.session['registro_ciudadano']

        login(request, user)
        messages.success(request, f'¡Bienvenido/a, {ciudadano.nombre}! Tu cuenta fue creada correctamente.')
        return redirect('portal:ciudadano_mi_perfil')


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


class CiudadanoPasswordResetView(PasswordResetView):
    form_class = CiudadanoPasswordResetForm
    template_name = 'portal/ciudadano/password_reset.html'
    email_template_name = 'portal/ciudadano/email/password_reset_body.html'
    subject_template_name = 'portal/ciudadano/email/password_reset_subject.txt'
    success_url = reverse_lazy('portal:ciudadano_password_reset_done')


class CiudadanoPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'portal/ciudadano/password_reset_done.html'


class CiudadanoPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'portal/ciudadano/password_reset_confirm.html'
    success_url = reverse_lazy('portal:ciudadano_password_reset_complete')


class CiudadanoPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'portal/ciudadano/password_reset_complete.html'


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
