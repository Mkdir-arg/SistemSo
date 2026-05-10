from datetime import date

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404

from portal.models import RecursoTurnos, TurnoCiudadano


def get_turnos_ciudadano_contexto(ciudadano):
    estados_cancelados_sistema = [
        TurnoCiudadano.Estado.CANCELADO_SISTEMA,
        TurnoCiudadano.Estado.REPROGRAMADO_SISTEMA,
    ]
    estados_cancelados_ciudadano = [
        TurnoCiudadano.Estado.CANCELADO_CIUDADANO,
        TurnoCiudadano.Estado.REPROGRAMADO_CIUDADANO,
    ]
    turnos_proximos_qs = TurnoCiudadano.objects.filter(
        ciudadano=ciudadano,
        fecha__gte=date.today(),
        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
    ).select_related(
        'configuracion',
        'configuracion__tipo_tramite',
        'recurso',
        'recurso__configuracion_turnos',
        'recurso__configuracion_turnos__tipo_tramite',
    ).order_by('fecha', 'hora_inicio')
    turnos_proximos = list(turnos_proximos_qs)

    def _tipo_tramite_id(turno):
        if getattr(turno, "configuracion_id", None):
            cfg_directa = getattr(turno, "configuracion", None)
            if cfg_directa and getattr(cfg_directa, "tipo_tramite_id", None):
                return cfg_directa.tipo_tramite_id
        cfg = getattr(turno, "config_efectiva", None)
        if cfg and getattr(cfg, "tipo_tramite_id", None):
            return cfg.tipo_tramite_id
        recurso_cfg = getattr(getattr(turno, "recurso", None), "configuracion_turnos", None)
        if recurso_cfg and getattr(recurso_cfg, "tipo_tramite_id", None):
            return recurso_cfg.tipo_tramite_id
        return None

    tipos_con_turno_vigente = {tid for tid in (_tipo_tramite_id(t) for t in turnos_proximos) if tid}

    cancelados_sistema_raw = list(
        TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            fecha__gte=date.today(),
            estado__in=estados_cancelados_sistema,
        ).select_related(
            'configuracion',
            'configuracion__tipo_tramite',
            'reemplazado_por_turno',
            'reemplazado_por_turno__configuracion',
            'reemplazado_por_turno__configuracion__tipo_tramite',
            'recurso',
            'recurso__configuracion_turnos',
            'recurso__configuracion_turnos__tipo_tramite',
        ).order_by('-fecha', '-hora_inicio')[:10]
    )
    turnos_cancelados_sistema = []
    cancelados_sistema_a_historial = []
    for turno in cancelados_sistema_raw:
        motivo = (turno.notas_backoffice or "").strip()
        lineas = [ln.strip() for ln in motivo.splitlines() if ln.strip()]
        motivo_legible = "Sin detalle informado."
        for ln in reversed(lineas):
            if "[CANCELACION_SISTEMA]" in ln:
                motivo_legible = ln.split("[CANCELACION_SISTEMA]", 1)[1].strip() or motivo_legible
                break
            if "[RECHAZO_SISTEMA]" in ln:
                motivo_legible = ln.split("[RECHAZO_SISTEMA]", 1)[1].strip() or motivo_legible
                break
        if motivo_legible == "Sin detalle informado." and lineas:
            motivo_legible = lineas[-1]
        turno.motivo_notificacion_cancelacion = motivo_legible
        reemplazo_vigente = (
            getattr(turno, "reemplazado_por_turno_id", None)
            and getattr(turno, "reemplazado_por_turno", None)
            and turno.reemplazado_por_turno.estado in [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO]
            and turno.reemplazado_por_turno.fecha >= date.today()
        )
        if reemplazo_vigente or _tipo_tramite_id(turno) in tipos_con_turno_vigente:
            cancelados_sistema_a_historial.append(turno)
        else:
            turnos_cancelados_sistema.append(turno)

    # Evita duplicados en proximos: para un mismo tramite cancelado por sistema,
    # se muestra solo el mas reciente y el resto pasa a historial.
    cancelados_sistema_filtrados = []
    ultimo_por_tipo = {}
    sin_tipo = []
    for turno in turnos_cancelados_sistema:
        tipo_id = _tipo_tramite_id(turno)
        if tipo_id:
            previo = ultimo_por_tipo.get(tipo_id)
            if not previo:
                ultimo_por_tipo[tipo_id] = turno
            else:
                fecha_hora_actual = (turno.fecha, turno.hora_inicio or turno.hora_fin)
                fecha_hora_previa = (previo.fecha, previo.hora_inicio or previo.hora_fin)
                if fecha_hora_actual > fecha_hora_previa:
                    cancelados_sistema_a_historial.append(previo)
                    ultimo_por_tipo[tipo_id] = turno
                else:
                    cancelados_sistema_a_historial.append(turno)
        else:
            sin_tipo.append(turno)
    cancelados_sistema_filtrados.extend(ultimo_por_tipo.values())
    cancelados_sistema_filtrados.extend(sin_tipo)
    turnos_cancelados_sistema = sorted(
        cancelados_sistema_filtrados,
        key=lambda t: (t.fecha, t.hora_inicio),
        reverse=True,
    )[:5]

    turnos_historial_base = list(
        TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
        ).filter(
            Q(fecha__lt=date.today()) | Q(estado__in=estados_cancelados_ciudadano)
        ).select_related('recurso', 'recurso__configuracion_turnos', 'recurso__configuracion_turnos__tipo_tramite').order_by('-fecha', '-hora_inicio')[:20]
    )
    historial_por_id = {t.id: t for t in turnos_historial_base}
    for turno in cancelados_sistema_a_historial:
        historial_por_id.setdefault(turno.id, turno)
    turnos_historial = sorted(
        historial_por_id.values(),
        key=lambda t: (t.fecha, t.hora_inicio),
        reverse=True,
    )[:10]

    return {
        'turnos_proximos': turnos_proximos,
        'turnos_cancelados_sistema': turnos_cancelados_sistema,
        'turnos_historial': turnos_historial,
    }


def get_recursos_turnos_activos():
    return RecursoTurnos.objects.filter(activo=True).order_by('tipo', 'nombre')


def get_recurso_turnos_activo_or_404(recurso_id):
    return get_object_or_404(RecursoTurnos, pk=recurso_id, activo=True)


def get_turno_ciudadano_or_404(ciudadano, pk):
    return get_object_or_404(
        TurnoCiudadano.objects.select_related('recurso'),
        pk=pk,
        ciudadano=ciudadano,
    )
