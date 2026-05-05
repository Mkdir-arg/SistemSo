"""Selectores ORM para bandeja operativa del modulo de flujos."""

from urllib.parse import urlencode

from django.contrib.auth import get_user_model

from flujos.models import TareaFlujo
from legajos.models_programas import Programa


def get_assignable_users_queryset():
    User = get_user_model()
    return (
        User.objects.filter(
            is_active=True,
            groups__name__in=['programaOperar', 'programaConfigurar'],
        )
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )


def _find_node(definicion, nodo_id):
    for nodo in definicion.get('nodos', []):
        if nodo.get('id') == nodo_id:
            return nodo
    return None


def _get_outgoing_transitions(definicion, nodo_id):
    return [
        transicion
        for transicion in definicion.get('transiciones', [])
        if transicion.get('desde') == nodo_id
    ]


def _build_configured_resolution_schema(nodo, tarea=None):
    task_data = tarea.datos if tarea is not None and isinstance(tarea.datos, dict) else {}
    config = nodo.get('config') or {}
    ui_schema = task_data.get('ui_schema')
    if not isinstance(ui_schema, dict):
        ui_schema = config.get('ui')

    if isinstance(ui_schema, dict) and ui_schema.get('type') == 'form':
        actor = task_data.get('actor')
        if actor is None:
            actor = nodo.get('actor')
        surface = task_data.get('surface')
        if surface is None:
            surface = nodo.get('surface')
        return {
            'type': 'ui_form',
            'title': ui_schema.get('title') or nodo.get('nombre') or nodo.get('id'),
            'description': ui_schema.get('description', ''),
            'layout': ui_schema.get('layout', 'single_column'),
            'sections': ui_schema.get('sections', []),
            'submit': ui_schema.get('submit') or {'label': 'Guardar y continuar'},
            'actor': actor,
            'surface': surface or ['backoffice'],
        }

    formulario = config.get('formulario')
    if not isinstance(formulario, dict):
        return None

    if formulario.get('type') == 'choice_select':
        field_name = formulario['field_name']
        return {
            'type': 'choice_select',
            'field_name': field_name,
            'field_label': formulario.get('field_label') or field_name.replace('_', ' ').capitalize(),
            'required': formulario.get('required', True),
            'options': formulario.get('options', []),
            'placeholder': formulario.get('placeholder', 'Seleccionar una opcion'),
            'help_text': formulario.get('help_text', ''),
        }

    if formulario.get('type') == 'text_input':
        field_name = formulario['field_name']
        return {
            'type': 'text_input',
            'field_name': field_name,
            'field_label': formulario.get('field_label') or field_name.replace('_', ' ').capitalize(),
            'required': formulario.get('required', True),
            'multiline': formulario.get('multiline', False),
            'rows': formulario.get('rows', 4),
            'placeholder': formulario.get('placeholder', ''),
            'help_text': formulario.get('help_text', ''),
        }

    if formulario.get('type') != 'boolean_decision':
        return {'type': 'json'}

    field_name = formulario['field_name']
    field_label = formulario.get('field_label') or (
        'Aprobacion' if field_name == 'aprobado' else field_name.replace('_', ' ').capitalize()
    )
    return {
        'type': 'boolean_decision',
        'field_name': field_name,
        'field_label': field_label,
        'true_label': formulario.get('true_label') or ('Aprobar' if field_name == 'aprobado' else 'Si'),
        'false_label': formulario.get('false_label') or ('Rechazar' if field_name == 'aprobado' else 'No'),
        'include_observacion': formulario.get('include_observacion', True),
        'observacion_label': formulario.get('observacion_label', 'Observacion'),
        'observacion_required': formulario.get('observacion_required', False),
    }


def _build_resolution_schema(nodo, transiciones_salida):
    configured_schema = _build_configured_resolution_schema(nodo)
    if configured_schema:
        return configured_schema

    condicionales = [
        transicion for transicion in transiciones_salida if not transicion['es_libre']
    ]
    if len(condicionales) != 2:
        return {'type': 'json'}

    condiciones = [transicion['condicion'] or {} for transicion in condicionales]
    campos = {condicion.get('campo') for condicion in condiciones}
    operadores = {condicion.get('operador') for condicion in condiciones}
    valores = {condicion.get('valor') for condicion in condiciones}

    if len(campos) != 1 or operadores != {'=='} or valores != {True, False}:
        return {'type': 'json'}

    field_name = next(iter(campos))
    field_label = 'Aprobacion' if field_name == 'aprobado' else field_name.replace('_', ' ').capitalize()
    return {
        'type': 'boolean_decision',
        'field_name': field_name,
        'field_label': field_label,
        'true_label': 'Aprobar' if field_name == 'aprobado' else 'Si',
        'false_label': 'Rechazar' if field_name == 'aprobado' else 'No',
        'include_observacion': True,
        'observacion_label': 'Observacion',
        'observacion_required': False,
    }


def enrich_tarea_runtime_metadata(tarea):
    definicion = tarea.instancia.version_flujo.definicion or {}
    nodo = _find_node(definicion, tarea.nodo_id) or {}
    transiciones_salida = []
    campos_requeridos = []
    tiene_salida_libre = False

    for transicion in _get_outgoing_transitions(definicion, tarea.nodo_id):
        condicion = transicion.get('condicion')
        es_libre = condicion is None
        if es_libre:
            tiene_salida_libre = True
        elif condicion.get('campo') and condicion['campo'] not in campos_requeridos:
            campos_requeridos.append(condicion['campo'])

        transiciones_salida.append(
            {
                'hasta': transicion.get('hasta'),
                'condicion': condicion,
                'es_libre': es_libre,
            }
        )

    resolution_schema = _build_configured_resolution_schema(nodo, tarea=tarea)
    if resolution_schema is None:
        resolution_schema = _build_resolution_schema(nodo, transiciones_salida)
    requires_structured_input = resolution_schema.get('type') != 'json'

    tarea.nodo_actual_data = nodo
    tarea.transiciones_salida = transiciones_salida
    tarea.campos_requeridos = campos_requeridos
    tarea.puede_resolver = (
        tarea.estado == TareaFlujo.Estado.PENDIENTE
        and tiene_salida_libre
        and not requires_structured_input
    )
    tarea.requiere_payload = (
        tarea.estado == TareaFlujo.Estado.PENDIENTE
        and (
            requires_structured_input
            or (not tiene_salida_libre and bool(transiciones_salida))
        )
    )
    tarea.resolution_schema = resolution_schema
    return tarea


def _serialize_user_summary(user):
    if not user:
        return None

    return {
        'id': user.pk,
        'username': user.username,
        'nombre': user.get_full_name() or user.username,
    }


def get_bandeja_tareas_queryset(filters=None):
    filters = filters or {}
    estado = filters.get('estado') or TareaFlujo.Estado.PENDIENTE
    programa_id = filters.get('programa') or ''
    asignado = filters.get('asignado') or ''

    tareas_qs = TareaFlujo.objects.select_related(
        'instancia__inscripcion__ciudadano',
        'instancia__inscripcion__programa',
        'instancia__version_flujo__flujo',
        'asignado_a',
        'resuelto_por',
    )

    if estado != 'TODOS':
        tareas_qs = tareas_qs.filter(estado=estado)

    if programa_id:
        tareas_qs = tareas_qs.filter(instancia__inscripcion__programa_id=programa_id)

    if asignado == 'sin_asignar':
        tareas_qs = tareas_qs.filter(asignado_a__isnull=True)
    elif asignado:
        tareas_qs = tareas_qs.filter(asignado_a_id=asignado)

    return tareas_qs.order_by('-fecha_creacion', '-pk')


def serialize_tarea_bandeja_item(tarea):
    tarea = enrich_tarea_runtime_metadata(tarea)
    ciudadano = tarea.instancia.inscripcion.ciudadano
    programa = tarea.instancia.inscripcion.programa

    return {
        'id': tarea.pk,
        'nombre': tarea.nombre,
        'descripcion': tarea.descripcion,
        'estado': tarea.estado,
        'estado_label': tarea.get_estado_display(),
        'nodo_id': tarea.nodo_id,
        'fecha_creacion': tarea.fecha_creacion.isoformat(),
        'fecha_resolucion': tarea.fecha_resolucion.isoformat() if tarea.fecha_resolucion else None,
        'programa': {
            'id': programa.pk,
            'codigo': programa.codigo,
            'nombre': programa.nombre,
        },
        'ciudadano': {
            'id': ciudadano.pk,
            'dni': ciudadano.dni,
            'nombre_completo': f'{ciudadano.nombre} {ciudadano.apellido}'.strip(),
        },
        'instancia': {
            'id': tarea.instancia_id,
            'estado': tarea.instancia.estado,
            'nodo_actual': tarea.instancia.nodo_actual,
            'datos': tarea.instancia.datos,
        },
        'flujo': {
            'nombre': tarea.instancia.version_flujo.flujo.nombre,
            'version': tarea.instancia.version_flujo.numero_version,
        },
        'asignado_a': _serialize_user_summary(tarea.asignado_a),
        'resuelto_por': _serialize_user_summary(tarea.resuelto_por),
        'puede_resolver': tarea.puede_resolver,
        'requiere_payload': tarea.requiere_payload,
        'campos_requeridos': tarea.campos_requeridos,
        'transiciones_salida': tarea.transiciones_salida,
    }


def serialize_instancia_log(log):
    return {
        'id': log.pk,
        'timestamp': log.timestamp.isoformat(),
        'nodo_desde': log.nodo_desde,
        'nodo_hasta': log.nodo_hasta,
        'motivo': log.motivo,
        'usuario': _serialize_user_summary(log.usuario),
        'datos_transicion': log.datos_transicion,
    }


def serialize_tarea_detalle_item(tarea):
    tarea = enrich_tarea_runtime_metadata(tarea)
    payload = serialize_tarea_bandeja_item(tarea)
    payload['nodo'] = tarea.nodo_actual_data
    payload['resolution_form'] = tarea.resolution_schema
    payload['acciones'] = {
        'puede_asignar': tarea.estado == TareaFlujo.Estado.PENDIENTE,
        'puede_resolver': tarea.estado == TareaFlujo.Estado.PENDIENTE,
    }
    return payload


def _build_bandeja_querystring(filtros):
    params = {
        key: value
        for key, value in filtros.items()
        if value and value != 'TODOS'
    }
    return urlencode(params)


def build_bandeja_tareas_context(filters=None):
    filters = filters or {}
    filtros = {
        'programa': filters.get('programa') or '',
        'asignado': filters.get('asignado') or '',
        'estado': filters.get('estado') or TareaFlujo.Estado.PENDIENTE,
    }

    tareas = [
        enrich_tarea_runtime_metadata(tarea)
        for tarea in get_bandeja_tareas_queryset(filtros)
    ]

    User = get_user_model()
    usuarios_ids = list(
        TareaFlujo.objects.exclude(asignado_a__isnull=True)
        .values_list('asignado_a_id', flat=True)
        .distinct()
    )

    programas_filter = Programa.objects.filter(
        inscripciones__instancia_flujo__tareas__isnull=False
    ).distinct().order_by('nombre')
    usuarios_asignados_filter = User.objects.filter(pk__in=usuarios_ids).order_by(
        'first_name', 'last_name', 'username'
    )
    estados_filter = [('TODOS', 'Todos')] + list(TareaFlujo.Estado.choices)

    programa_labels = {
        str(programa.pk): f'{programa.nombre} ({programa.codigo})'
        for programa in programas_filter
    }
    usuario_labels = {
        str(usuario.pk): usuario.get_full_name() or usuario.username
        for usuario in usuarios_asignados_filter
    }
    estado_labels = {value: label for value, label in estados_filter}

    filtros_resumen = []
    if filtros['programa']:
        filtros_resumen.append(
            f"Programa: {programa_labels.get(filtros['programa'], filtros['programa'])}"
        )
    if filtros['asignado']:
        filtros_resumen.append(
            'Asignado: Sin asignar'
            if filtros['asignado'] == 'sin_asignar'
            else f"Asignado: {usuario_labels.get(filtros['asignado'], filtros['asignado'])}"
        )
    if filtros['estado'] and filtros['estado'] != 'TODOS':
        filtros_resumen.append(
            f"Estado: {estado_labels.get(filtros['estado'], filtros['estado'])}"
        )

    return {
        'tareas': tareas,
        'total': len(tareas),
        'resolubles': sum(1 for tarea in tareas if tarea.puede_resolver),
        'bloqueadas': sum(1 for tarea in tareas if tarea.requiere_payload),
        'filtros': filtros,
        'filtros_activos': filtros_resumen,
        'bandeja_querystring': _build_bandeja_querystring(filtros),
        'usuarios_asignables': get_assignable_users_queryset(),
        'programas_filter': programas_filter,
        'usuarios_asignados_filter': usuarios_asignados_filter,
        'estados_filter': estados_filter,
    }