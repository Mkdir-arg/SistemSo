from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.decorators import group_required
from portal.models import TurnoCiudadano
from .forms import (
    AprobarTurnoForm,
    CancelarTurnoBackofficeForm,
    ConfiguracionTurnosForm,
    DisponibilidadConfiguracionForm,
    RechazarTurnoForm,
)
from .models import ConfiguracionTurnos, DisponibilidadConfiguracion
from .selectors_turnos import (
    build_agenda_context,
    build_bandeja_pendientes_context,
    get_backoffice_home_context,
    get_configuraciones_list,
    get_turno_detalle_queryset,
)
from .services_turnos import TurnoActionError, TurnosBackofficeService


def _es_operador(user):
    return user.is_authenticated and (
        user.is_staff or user.is_superuser or
        not user.groups.filter(name='Ciudadanos').exists()
    )


def _operador_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not _es_operador(request.user):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped)


def _admin_turnos_required(view_func):
    return login_required(
        group_required(['Administradores de Turnos'])(view_func)
    )


# ─── Dashboard ───────────────────────────────────────────────────────────────

@_operador_required
def backoffice_home(request):
    return render(
        request,
        'turnos/backoffice/home.html',
        get_backoffice_home_context(),
    )


# ─── Configuraciones ─────────────────────────────────────────────────────────

@_operador_required
def configuracion_lista(request):
    return render(
        request,
        'turnos/backoffice/configuracion_lista.html',
        {'configs': get_configuraciones_list()},
    )


@_admin_turnos_required
def configuracion_crear(request):
    if request.method == 'POST':
        form = ConfiguracionTurnosForm(request.POST)
        if form.is_valid():
            config = form.save()
            messages.success(request, f'Configuración "{config.nombre}" creada correctamente.')
            return redirect('turnos:disponibilidad_grilla', pk=config.pk)
    else:
        form = ConfiguracionTurnosForm()
    return render(request, 'turnos/backoffice/configuracion_form.html', {
        'form': form,
        'titulo': 'Nueva configuración de turnos',
        'accion': 'Crear',
    })


@_admin_turnos_required
def configuracion_editar(request, pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    if request.method == 'POST':
        form = ConfiguracionTurnosForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración actualizada correctamente.')
            return redirect('turnos:disponibilidad_grilla', pk=config.pk)
    else:
        form = ConfiguracionTurnosForm(instance=config)
    return render(request, 'turnos/backoffice/configuracion_form.html', {
        'form': form,
        'config': config,
        'titulo': f'Editar: {config.nombre}',
        'accion': 'Guardar cambios',
    })


# ─── Disponibilidad (grilla semanal) ─────────────────────────────────────────

@_admin_turnos_required
def disponibilidad_grilla(request, pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    disponibilidades = config.disponibilidades.all()

    # Organizar por día para la grilla
    por_dia = {i: [] for i in range(7)}
    for disp in disponibilidades:
        por_dia[disp.dia_semana].append(disp)

    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    return render(request, 'turnos/backoffice/disponibilidad_grilla.html', {
        'config': config,
        'por_dia': por_dia,
        'dias': list(enumerate(dias)),
    })


@_admin_turnos_required
def disponibilidad_agregar(request, pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)

    if request.method == 'POST':
        form = DisponibilidadConfiguracionForm(request.POST)
        if form.is_valid():
            disp = form.save(commit=False)
            disp.configuracion = config

            # Verificar unicidad (configuracion + dia_semana + hora_inicio)
            existe = DisponibilidadConfiguracion.objects.filter(
                configuracion=config,
                dia_semana=disp.dia_semana,
                hora_inicio=disp.hora_inicio,
            ).exists()
            if existe:
                form.add_error('hora_inicio', 'Ya existe una franja para ese día y horario.')
                return render(request, 'turnos/backoffice/disponibilidad_form.html', {
                    'form': form, 'config': config, 'titulo': 'Agregar franja horaria',
                })

            disp.save()
            cd = form.cleaned_data
            slots = cd.get('_slots_preview', '?')
            resto = cd.get('_resto_min', 0)
            msg = f'Franja agregada. Se generarán {slots} turnos de {disp.duracion_turno_min} min.'
            if resto:
                msg += f' Quedan {resto} min sin cubrir.'
            messages.success(request, msg)
            return redirect('turnos:disponibilidad_grilla', pk=config.pk)
    else:
        dia = request.GET.get('dia')
        initial = {'dia_semana': dia} if dia else {}
        form = DisponibilidadConfiguracionForm(initial=initial)

    return render(request, 'turnos/backoffice/disponibilidad_form.html', {
        'form': form,
        'config': config,
        'titulo': 'Agregar franja horaria',
    })


@_admin_turnos_required
def disponibilidad_editar(request, pk, disp_pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    disp = get_object_or_404(DisponibilidadConfiguracion, pk=disp_pk, configuracion=config)

    if request.method == 'POST':
        form = DisponibilidadConfiguracionForm(request.POST, instance=disp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Franja horaria actualizada.')
            return redirect('turnos:disponibilidad_grilla', pk=config.pk)
    else:
        form = DisponibilidadConfiguracionForm(instance=disp)

    return render(request, 'turnos/backoffice/disponibilidad_form.html', {
        'form': form,
        'config': config,
        'disp': disp,
        'titulo': 'Editar franja horaria',
    })


@_admin_turnos_required
@require_POST
def disponibilidad_eliminar(request, pk, disp_pk):
    config = get_object_or_404(ConfiguracionTurnos, pk=pk)
    disp = get_object_or_404(DisponibilidadConfiguracion, pk=disp_pk, configuracion=config)

    # Verificar que no haya turnos futuros en esa franja
    from portal.models import TurnoCiudadano
    turnos_afectados = TurnoCiudadano.objects.filter(
        configuracion=config,
        fecha__gte=date.today(),
        hora_inicio=disp.hora_inicio,
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).count()

    if turnos_afectados:
        messages.error(
            request,
            f'No se puede eliminar: hay {turnos_afectados} turno(s) futuro(s) en ese horario.',
        )
        return redirect('turnos:disponibilidad_grilla', pk=config.pk)

    disp.delete()
    messages.success(request, 'Franja horaria eliminada.')
    return redirect('turnos:disponibilidad_grilla', pk=config.pk)


# ─── Agenda ──────────────────────────────────────────────────────────────────

@_operador_required
def agenda(request):
    hoy = date.today()
    fecha_str = request.GET.get('fecha', hoy.isoformat())
    config_id = request.GET.get('config')

    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        fecha = hoy

    estado_filter = request.GET.get('estado')
    return render(
        request,
        'turnos/backoffice/agenda.html',
        build_agenda_context(fecha, config_id=config_id, estado_filter=estado_filter),
    )


# ─── Bandeja de pendientes ────────────────────────────────────────────────────

@_operador_required
def bandeja_pendientes(request):
    return render(
        request,
        'turnos/backoffice/bandeja_pendientes.html',
        build_bandeja_pendientes_context(),
    )


# ─── Detalle de turno ─────────────────────────────────────────────────────────

@_operador_required
def turno_detalle(request, pk):
    turno = get_object_or_404(get_turno_detalle_queryset(), pk=pk)

    if request.method == 'POST' and 'notas_backoffice' in request.POST:
        TurnosBackofficeService.actualizar_notas(
            turno, request.POST.get('notas_backoffice', '')
        )
        messages.success(request, 'Notas actualizadas.')
        return redirect('turnos:turno_detalle', pk=pk)

    context = {
        'turno': turno,
        'form_aprobar': AprobarTurnoForm(),
        'form_rechazar': RechazarTurnoForm(),
        'form_cancelar': CancelarTurnoBackofficeForm(),
        'puede_aprobar': turno.estado == TurnoCiudadano.Estado.PENDIENTE,
        'puede_completar': turno.estado == TurnoCiudadano.Estado.CONFIRMADO and turno.fecha <= date.today(),
        'puede_cancelar': turno.estado in [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    }
    return render(request, 'turnos/backoffice/turno_detalle.html', context)


# ─── Acciones sobre turnos ────────────────────────────────────────────────────

@_operador_required
@require_POST
def turno_aprobar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)

    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return redirect('turnos:turno_detalle', pk=pk)

    form = AprobarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Datos inválidos.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.aprobar_turno(
            pk, request.user, notas=form.cleaned_data.get('notas', '')
        )
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(
        request,
        f'Turno {turno.codigo_turno} confirmado. Se notificó al ciudadano por email.',
    )
    return redirect(request.POST.get('next', 'turnos:bandeja_pendientes'))


@_operador_required
@require_POST
def turno_rechazar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)

    if turno.estado != TurnoCiudadano.Estado.PENDIENTE:
        messages.warning(request, 'Este turno ya fue procesado.')
        return redirect('turnos:turno_detalle', pk=pk)

    form = RechazarTurnoForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de rechazo.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.rechazar_turno(
            pk, request.user, form.cleaned_data['motivo']
        )
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(request, f'Turno {turno.codigo_turno} rechazado. Se notificó al ciudadano.')
    return redirect(request.POST.get('next', 'turnos:bandeja_pendientes'))


@_operador_required
@require_POST
def turno_cancelar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)

    form = CancelarTurnoBackofficeForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Debe ingresar un motivo de cancelación.')
        return redirect('turnos:turno_detalle', pk=pk)

    try:
        turno = TurnosBackofficeService.cancelar_turno(
            turno, form.cleaned_data['motivo']
        )
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)

    messages.success(request, f'Turno {turno.codigo_turno} cancelado. Se notificó al ciudadano.')
    return redirect('turnos:agenda')


@_operador_required
@require_POST
def turno_completar(request, pk):
    turno = get_object_or_404(TurnoCiudadano, pk=pk)
    try:
        turno = TurnosBackofficeService.completar_turno(turno)
    except TurnoActionError as exc:
        messages.warning(request, str(exc))
        return redirect('turnos:turno_detalle', pk=pk)
    messages.success(request, f'Turno {turno.codigo_turno} marcado como completado.')
    return redirect(request.POST.get('next', 'turnos:agenda'))


# ─── API interna (Alpine.js) ──────────────────────────────────────────────────

@login_required
def api_slots_configuracion(request):
    if not _es_operador(request.user):
        return JsonResponse({'error': 'Sin permiso'}, status=403)

    config_id = request.GET.get('config_id')
    fecha_str = request.GET.get('fecha')

    try:
        config = ConfiguracionTurnos.objects.get(pk=config_id, activo=True)
        fecha = date.fromisoformat(fecha_str)
    except (ConfiguracionTurnos.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    from .turnos_utils import get_slots_por_configuracion
    slots = get_slots_por_configuracion(config, fecha)

    return JsonResponse({'slots': [
        {
            'hora_inicio': s['hora_inicio'].strftime('%H:%M'),
            'hora_fin': s['hora_fin'].strftime('%H:%M'),
            'disponible': s['disponible'],
            'cupo_restante': s['cupo_restante'],
        }
        for s in slots
    ]})
