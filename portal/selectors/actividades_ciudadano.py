"""
Selector de actividades accesibles para un ciudadano en el portal.
"""
from django.db.models import Q


def get_actividades_accesibles(ciudadano, institucion=None):
    """
    Retorna las actividades que un ciudadano puede ver/solicitar inscripción.

    - Actividades LIBRE: siempre accesibles.
    - Actividades REQUIERE_PROGRAMA: solo si el ciudadano tiene InscripcionPrograma
      con estado ACTIVO o EN_SEGUIMIENTO en el programa requerido.

    Si se pasa 'institucion', filtra además por legajo_institucional__institucion.

    Usa 2 queries independientemente de la cantidad de actividades (anti N+1).
    """
    from legajos.models import PlanFortalecimiento
    from legajos.models_programas import InscripcionPrograma

    # IDs de programas en los que el ciudadano está activo
    programas_activos = set(
        InscripcionPrograma.objects.filter(
            ciudadano=ciudadano,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
        ).values_list('programa_id', flat=True)
    )

    qs = PlanFortalecimiento.objects.filter(
        estado=PlanFortalecimiento.Estado.ACTIVO,
    ).select_related('programa_requerido', 'legajo_institucional__institucion')

    if institucion is not None:
        qs = qs.filter(legajo_institucional__institucion=institucion)

    qs = qs.filter(
        Q(tipo_acceso=PlanFortalecimiento.TipoAcceso.LIBRE)
        | Q(
            tipo_acceso=PlanFortalecimiento.TipoAcceso.REQUIERE_PROGRAMA,
            programa_requerido_id__in=programas_activos,
        )
    )

    return qs.order_by('nombre')


def get_inscripciones_ciudadano(ciudadano):
    """
    Retorna todas las inscripciones del ciudadano (historial completo, cualquier estado),
    ordenadas por fecha descendente.
    """
    from legajos.models import InscriptoActividad

    return InscriptoActividad.objects.filter(
        ciudadano=ciudadano,
    ).select_related(
        'actividad',
        'actividad__legajo_institucional__institucion',
    ).order_by('-fecha_inscripcion')
