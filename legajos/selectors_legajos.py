from django.db.models import Count, Q

from .models import LegajoAtencion


def get_legajos_queryset(estado=""):
    queryset = LegajoAtencion.objects.select_related(
        'ciudadano',
        'dispositivo',
        'responsable',
    )
    if estado:
        queryset = queryset.filter(estado=estado)
    return queryset.order_by('-fecha_apertura')


def get_legajo_detail_queryset():
    return LegajoAtencion.objects.select_related(
        'ciudadano',
        'dispositivo',
        'responsable',
        'evaluacion',
    ).prefetch_related(
        'seguimientos__profesional__usuario',
        'eventos',
    )


def get_planes_queryset(legajo):
    return legajo.planes.select_related('profesional__usuario').order_by('-creado')


def get_plan_vigente(legajo):
    return legajo.planes.filter(vigente=True).select_related('profesional__usuario').first()


def get_seguimientos_queryset(legajo, tipo=""):
    queryset = legajo.seguimientos.select_related('profesional__usuario')
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    return queryset


def get_seguimientos_dashboard_metrics(legajo):
    return legajo.seguimientos.aggregate(
        total_seguimientos=Count('id'),
        entrevistas_count=Count('id', filter=Q(tipo='ENTREVISTA')),
        visitas_count=Count('id', filter=Q(tipo='VISITA')),
        llamadas_count=Count('id', filter=Q(tipo='LLAMADA')),
    )


def get_derivaciones_queryset(legajo, estado=""):
    queryset = legajo.derivaciones.select_related('destino', 'actividad_destino')
    if estado:
        queryset = queryset.filter(estado=estado)
    return queryset
