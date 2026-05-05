"""
API JSON para el motor de flujos (US-006).
Endpoints sin DRF — FBVs que devuelven JsonResponse.
"""
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from core.decorators import group_required
from legajos.models_programas import Programa
from system_modules.guards import module_required

from flujos.application.services import (
    FlowTaskActionError,
    asignar_tarea_flujo,
    resolver_tarea_flujo,
)
from flujos.infrastructure.selectors import (
    build_bandeja_tareas_context,
    enrich_tarea_runtime_metadata,
    get_assignable_users_queryset,
    get_bandeja_tareas_queryset,
    serialize_instancia_log,
    serialize_tarea_bandeja_item,
    serialize_tarea_detalle_item,
)
from .forms import (
    DefinicionFlujoForm,
    TareaAsignacionForm,
    TareaResolverForm,
    build_tarea_resolution_form,
)
from flujos.models import Flujo, InstanciaFlujo, TareaFlujo, VersionFlujo

logger = logging.getLogger(__name__)


def _tiene_permiso_editar(user):
    return user.groups.filter(name='programaConfigurar').exists() or user.is_superuser


def _tiene_permiso_operar(user):
    return user.groups.filter(name__in=['programaConfigurar', 'programaOperar']).exists() or user.is_superuser


def _extract_bandeja_filters(request):
    estado = request.GET.get('estado') or TareaFlujo.Estado.PENDIENTE
    programa = (request.GET.get('programa') or '').strip()
    asignado = (request.GET.get('asignado') or '').strip()

    estados_validos = {choice for choice, _ in TareaFlujo.Estado.choices}
    estados_validos.add('TODOS')
    if estado not in estados_validos:
        estado = TareaFlujo.Estado.PENDIENTE

    if programa and not programa.isdigit():
        programa = ''

    if asignado and asignado != 'sin_asignar' and not asignado.isdigit():
        asignado = ''

    return {
        'programa': programa,
        'asignado': asignado,
        'estado': estado,
    }


def _build_tarea_asignacion_message(tarea, usuario_asignado):
    if usuario_asignado is None:
        return f'Tarea "{tarea.nombre}" desasignada correctamente.'
    nombre = usuario_asignado.get_full_name() or usuario_asignado.username
    return f'Tarea "{tarea.nombre}" asignada a {nombre}.'


@login_required
@require_http_methods(['GET', 'POST'])
@module_required("flujos")
def api_definicion(request, programa_id):
    programa = get_object_or_404(Programa, pk=programa_id)

    if request.method == 'GET':
        try:
            flujo = programa.flujo
        except Flujo.DoesNotExist:
            return JsonResponse({'definicion': None, 'version': None})

        version = flujo.versiones.filter(estado=VersionFlujo.Estado.PUBLICADA).order_by('-numero_version').first()
        if not version:
            version = flujo.versiones.order_by('-numero_version').first()
        if not version:
            return JsonResponse({'definicion': None, 'version': None})

        return JsonResponse({
            'definicion': version.definicion,
            'version_id': version.pk,
            'numero_version': version.numero_version,
            'estado': version.estado,
        })

    # POST — guardar nueva versión borrador
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON inválido.'}, status=400)

    form = DefinicionFlujoForm({'definicion': body})
    if not form.is_valid():
        return JsonResponse({'error': form.errors['definicion'][0]}, status=400)

    flujo, _ = Flujo.objects.get_or_create(
        programa=programa,
        defaults={'nombre': f'Flujo — {programa.nombre}'},
    )
    version = VersionFlujo.objects.create(
        flujo=flujo,
        definicion=form.cleaned_data['definicion'],
        creado_por=request.user,
    )

    return JsonResponse({
        'ok': True,
        'version_id': version.pk,
        'numero_version': version.numero_version,
    })


@login_required
@require_http_methods(['POST'])
@module_required("flujos")
def api_publicar(request, programa_id):
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    programa = get_object_or_404(Programa, pk=programa_id)

    try:
        flujo = programa.flujo
    except Flujo.DoesNotExist:
        return JsonResponse({'error': 'El programa no tiene flujo definido.'}, status=400)

    from django.db import transaction
    with transaction.atomic():
        borrador = (
            flujo.versiones
            .select_for_update()
            .filter(estado=VersionFlujo.Estado.BORRADOR)
            .order_by('-numero_version')
            .first()
        )
        if not borrador:
            return JsonResponse({'error': 'No hay versión borrador para publicar.'}, status=400)

        form = DefinicionFlujoForm(
            {'definicion': borrador.definicion},
            validation_mode='publish',
        )
        if not form.is_valid():
            return JsonResponse({'error': form.errors['definicion'][0]}, status=400)

        borrador.definicion = form.cleaned_data['definicion']

        flujo.versiones.filter(estado=VersionFlujo.Estado.PUBLICADA).update(
            estado=VersionFlujo.Estado.ARCHIVADA
        )
        borrador.estado = VersionFlujo.Estado.PUBLICADA
        borrador.fecha_publicacion = timezone.now()
        borrador.save(update_fields=['definicion', 'estado', 'fecha_publicacion'])

    return JsonResponse({'ok': True, 'version_id': borrador.pk})


@login_required
@require_http_methods(['GET'])
@module_required("flujos")
def api_instancia(request, instancia_id):
    if not _tiene_permiso_editar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    instancia = get_object_or_404(InstanciaFlujo, pk=instancia_id)

    definicion = instancia.version_flujo.definicion
    nodo = next(
        (n for n in definicion.get('nodos', []) if n['id'] == instancia.nodo_actual),
        None,
    )

    return JsonResponse({
        'instancia_id': instancia.pk,
        'nodo_actual': instancia.nodo_actual,
        'nodo': nodo,
        'estado': instancia.estado,
        'fecha_inicio': instancia.fecha_inicio.isoformat(),
        'fecha_cierre': instancia.fecha_cierre.isoformat() if instancia.fecha_cierre else None,
    })


@login_required
@require_http_methods(['GET'])
@module_required("flujos")
def api_bandeja_tareas(request):
    if not _tiene_permiso_operar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    context = build_bandeja_tareas_context(_extract_bandeja_filters(request))
    return JsonResponse(
        {
            'results': [
                serialize_tarea_bandeja_item(tarea)
                for tarea in context['tareas']
            ],
            'summary': {
                'total': context['total'],
                'resolubles': context['resolubles'],
                'bloqueadas': context['bloqueadas'],
            },
            'filters': {
                'applied': context['filtros'],
                'programas': [
                    {
                        'id': programa.pk,
                        'nombre': programa.nombre,
                        'codigo': programa.codigo,
                    }
                    for programa in context['programas_filter']
                ],
                'asignados': [
                    {
                        'id': usuario.pk,
                        'username': usuario.username,
                        'nombre': usuario.get_full_name() or usuario.username,
                    }
                    for usuario in context['usuarios_asignados_filter']
                ],
                'estados': [
                    {'value': value, 'label': label}
                    for value, label in context['estados_filter']
                ],
            },
        }
    )


@login_required
@require_http_methods(['POST'])
@module_required("flujos")
def api_tarea_asignar(request, pk):
    if not _tiene_permiso_operar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )

    try:
        body = json.loads(request.body or '{}')
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON invalido.'}, status=400)

    form = TareaAsignacionForm(body)
    if not form.is_valid():
        return JsonResponse({'error': 'La asignacion indicada no es valida.'}, status=400)

    try:
        tarea = asignar_tarea_flujo(
            tarea=tarea,
            usuario_asignado=form.cleaned_data['asignado_a'],
            usuario_actor=request.user,
        )
    except FlowTaskActionError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    return JsonResponse(
        {
            'ok': True,
            'message': _build_tarea_asignacion_message(
                tarea,
                form.cleaned_data['asignado_a'],
            ),
            'task': serialize_tarea_bandeja_item(tarea),
        }
    )


@login_required
@require_http_methods(['POST'])
@module_required("flujos")
def api_tarea_resolver(request, pk):
    if not _tiene_permiso_operar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )

    try:
        body = json.loads(request.body or '{}')
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'JSON invalido.'}, status=400)

    form = TareaResolverForm({'datos': body.get('datos', {})})
    if not form.is_valid():
        return JsonResponse({'error': 'Los datos de resolucion no tienen un JSON valido.'}, status=400)

    try:
        instancia = resolver_tarea_flujo(
            tarea=tarea,
            usuario=request.user,
            datos=form.cleaned_data['datos'],
        )
    except FlowTaskActionError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )
    return JsonResponse(
        {
            'ok': True,
            'message': f'Tarea "{tarea.nombre}" resuelta correctamente.',
            'task': serialize_tarea_bandeja_item(tarea),
            'instance': {
                'id': instancia.pk,
                'estado': instancia.estado,
                'nodo_actual': instancia.nodo_actual,
                'fecha_cierre': instancia.fecha_cierre.isoformat() if instancia.fecha_cierre else None,
                'datos': instancia.datos,
            },
        }
    )


@login_required
@require_http_methods(['GET'])
@module_required("flujos")
def api_tarea_detalle(request, pk):
    if not _tiene_permiso_operar(request.user):
        return JsonResponse({'error': 'Sin permiso.'}, status=403)

    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )

    timeline = [
        serialize_instancia_log(log)
        for log in tarea.instancia.logs.select_related('usuario').order_by('-timestamp', '-pk')
    ]

    return JsonResponse(
        {
            'task': serialize_tarea_detalle_item(tarea),
            'timeline': timeline,
            'assignable_users': [
                {
                    'id': usuario.pk,
                    'username': usuario.username,
                    'nombre': usuario.get_full_name() or usuario.username,
                }
                for usuario in get_assignable_users_queryset()
            ],
            'links': {
                'assign': reverse('flujos:api_tarea_asignar', args=[tarea.pk]),
                'resolve': reverse('flujos:api_tarea_resolver', args=[tarea.pk]),
            },
        }
    )


# ---------------------------------------------------------------------------
# Editor visual (US-007)
# ---------------------------------------------------------------------------

@login_required
@group_required(['programaConfigurar'])
@module_required("flujos")
def editor_flujo(request, programa_id):
    programa = get_object_or_404(Programa, pk=programa_id)
    flujo = None
    cantidad_versiones = 0
    version_publicada = None
    ultima_version = None
    hay_borrador = False

    try:
        flujo = programa.flujo
    except ObjectDoesNotExist:
        flujo = None

    if flujo is not None:
        versiones = flujo.versiones.all()
        cantidad_versiones = versiones.count()
        version_publicada = versiones.filter(
            estado=VersionFlujo.Estado.PUBLICADA,
        ).order_by('-numero_version').first()
        ultima_version = versiones.order_by('-numero_version').first()
        hay_borrador = versiones.filter(estado=VersionFlujo.Estado.BORRADOR).exists()

    instancias_activas = 0
    try:
        version_publicada = programa.flujo_activo
        if version_publicada:
            from flujos.models import InstanciaFlujo as _IF
            instancias_activas = _IF.objects.filter(
                version_flujo=version_publicada,
                estado=_IF.Estado.ACTIVA,
            ).count()
    except Exception:
        pass

    return render(request, 'flujos/editor.html', {
        'programa': programa,
        'cantidad_versiones': cantidad_versiones,
        'instancias_activas': instancias_activas,
        'version_publicada': version_publicada,
        'ultima_version': ultima_version,
        'hay_borrador': hay_borrador,
        'api_definicion_url': reverse('flujos:api_definicion', kwargs={'programa_id': programa_id}),
        'api_publicar_url': reverse('flujos:api_publicar', kwargs={'programa_id': programa_id}),
    })


@login_required
@group_required(['programaConfigurar', 'programaOperar'])
@module_required("flujos")
def bandeja_tareas(request):
    return render(
        request,
        'flujos/backoffice/bandeja_tareas.html',
        build_bandeja_tareas_context(_extract_bandeja_filters(request)),
    )


@login_required
@group_required(['programaConfigurar', 'programaOperar'])
@require_http_methods(['GET', 'POST'])
@module_required("flujos")
def tarea_detalle(request, pk):
    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )
    enrich_tarea_runtime_metadata(tarea)

    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or reverse('flujos_editor:bandeja_tareas')
    )
    form = build_tarea_resolution_form(
        tarea=tarea,
        data=request.POST or None,
        initial_runtime_data=tarea.instancia.datos or {},
    )

    if request.method == 'POST':
        if tarea.estado != TareaFlujo.Estado.PENDIENTE:
            form.add_error(None, 'La tarea ya fue procesada y quedó solo de consulta.')
        elif form.is_valid():
            try:
                resolver_tarea_flujo(
                    tarea=tarea,
                    usuario=request.user,
                    datos=form.to_runtime_data(),
                )
            except FlowTaskActionError as exc:
                form.add_error(None, str(exc))
            else:
                messages.success(request, f'Tarea "{tarea.nombre}" resuelta correctamente.')
                return redirect(next_url)

    return render(
        request,
        'flujos/backoffice/tarea_detalle.html',
        {
            'tarea': tarea,
            'form': form,
            'resolution_schema': getattr(tarea, 'resolution_schema', {'type': 'json'}),
            'timeline': [
                serialize_instancia_log(log)
                for log in tarea.instancia.logs.select_related('usuario').order_by('-timestamp', '-pk')
            ],
            'asignacion_form': TareaAsignacionForm(initial={'asignado_a': tarea.asignado_a}),
            'usuarios_asignables': get_assignable_users_queryset(),
            'next_url': next_url,
        },
    )


@login_required
@group_required(['programaConfigurar', 'programaOperar'])
@require_POST
@module_required("flujos")
def tarea_asignar(request, pk):
    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )
    form = TareaAsignacionForm(request.POST)

    if not form.is_valid():
        messages.warning(request, 'La asignación indicada no es válida.')
        return redirect(request.POST.get('next', 'flujos_editor:bandeja_tareas'))

    try:
        asignar_tarea_flujo(
            tarea=tarea,
            usuario_asignado=form.cleaned_data['asignado_a'],
            usuario_actor=request.user,
        )
    except FlowTaskActionError as exc:
        messages.warning(request, str(exc))
    else:
        messages.success(
            request,
            _build_tarea_asignacion_message(tarea, form.cleaned_data['asignado_a']),
        )

    return redirect(request.POST.get('next', 'flujos_editor:bandeja_tareas'))


@login_required
@group_required(['programaConfigurar', 'programaOperar'])
@require_POST
@module_required("flujos")
def tarea_resolver(request, pk):
    tarea = get_object_or_404(
        get_bandeja_tareas_queryset({'estado': 'TODOS'}),
        pk=pk,
    )
    form = TareaResolverForm(request.POST)

    if not form.is_valid():
        messages.warning(request, 'Los datos de resolución no tienen un JSON válido.')
        return redirect(request.POST.get('next', 'flujos_editor:bandeja_tareas'))

    try:
        resolver_tarea_flujo(
            tarea=tarea,
            usuario=request.user,
            datos=form.cleaned_data['datos'],
        )
    except FlowTaskActionError as exc:
        messages.warning(request, str(exc))
    else:
        messages.success(request, f'Tarea "{tarea.nombre}" resuelta correctamente.')

    return redirect(request.POST.get('next', 'flujos_editor:bandeja_tareas'))
