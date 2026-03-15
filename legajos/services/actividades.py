"""
Servicios para gestión de acceso a actividades institucionales.
"""


def validar_acceso_actividad(actividad, ciudadano):
    """
    Verifica si un ciudadano puede inscribirse a una actividad según su tipo de acceso.

    Returns:
        tuple[bool, str]: (puede_acceder, mensaje_error)
        - Si puede_acceder es True, mensaje_error es cadena vacía.
        - Si puede_acceder es False, mensaje_error describe el requisito faltante.
    """
    from ..models import PlanFortalecimiento
    from ..models_programas import InscripcionPrograma

    if actividad.tipo_acceso == PlanFortalecimiento.TipoAcceso.LIBRE:
        return True, ''

    # REQUIERE_PROGRAMA
    if not actividad.programa_requerido_id:
        # Mal configurada — no bloqueamos al ciudadano
        return True, ''

    tiene_inscripcion = InscripcionPrograma.objects.filter(
        ciudadano=ciudadano,
        programa_id=actividad.programa_requerido_id,
        estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
    ).exists()

    if tiene_inscripcion:
        return True, ''

    nombre_programa = actividad.programa_requerido.nombre if actividad.programa_requerido else ''
    return (
        False,
        f'Para acceder a esta actividad debés estar inscripto activo en el programa "{nombre_programa}".',
    )
