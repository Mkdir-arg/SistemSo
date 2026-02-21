"""
Vistas para Programa Ñachec - Bandejas y Formularios
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models_nachec import (
    CasoNachec, EstadoCaso, RelevamientoNachec, 
    EvaluacionVulnerabilidad, PlanIntervencionNachec,
    PrestacionNachec, TareaNachec, SeguimientoTerritorial
)
from .services_nachec import (
    ServicioTransicionNachec, ServicioDeteccionDuplicados, ServicioSLA
)
from .models import Ciudadano


# ============================================================================
# HELPERS - Verificación de roles
# ============================================================================

def es_operador(user):
    return user.groups.filter(name__in=['Operador', 'Operador Admisión']).exists() or user.is_superuser

def es_coordinador(user):
    return user.groups.filter(name__in=['Coordinador', 'Coordinador Ñachec']).exists() or user.is_superuser

def es_territorial(user):
    return user.groups.filter(name__in=['Territorial', 'Trabajador Territorial']).exists() or user.is_superuser

def es_evaluador(user):
    return user.groups.filter(name__in=['Evaluador', 'Profesional']).exists() or user.is_superuser

def es_referente(user):
    return user.groups.filter(name__in=['Referente', 'Referente Programa']).exists() or user.is_superuser


# ============================================================================
# BANDEJA 1: DERIVACIONES ENTRANTES (Operador)
# ============================================================================

@login_required
@user_passes_test(es_operador)
def bandeja_derivaciones(request):
    """Bandeja de derivaciones entrantes para operadores"""
    
    # Filtros
    estado = request.GET.get('estado', EstadoCaso.DERIVADO)
    municipio = request.GET.get('municipio', '')
    prioridad = request.GET.get('prioridad', '')
    busqueda = request.GET.get('q', '')
    
    # Query base
    casos = CasoNachec.objects.filter(
        estado__in=[EstadoCaso.DERIVADO, EstadoCaso.EN_REVISION]
    ).select_related('ciudadano_titular', 'operador_admision')
    
    # Aplicar filtros
    if estado:
        casos = casos.filter(estado=estado)
    if municipio:
        casos = casos.filter(municipio=municipio)
    if prioridad:
        casos = casos.filter(prioridad=prioridad)
    if busqueda:
        casos = casos.filter(
            Q(ciudadano_titular__nombre__icontains=busqueda) |
            Q(ciudadano_titular__apellido__icontains=busqueda) |
            Q(ciudadano_titular__dni__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(casos, 20)
    page = request.GET.get('page', 1)
    casos_page = paginator.get_page(page)
    
    # Municipios para filtro
    municipios = CasoNachec.objects.values_list('municipio', flat=True).distinct()
    
    context = {
        'casos': casos_page,
        'municipios': municipios,
        'total': casos.count(),
    }
    
    return render(request, 'nachec/bandeja_derivaciones.html', context)


@login_required
@user_passes_test(es_operador)
def detalle_derivacion(request, caso_id):
    """Detalle de derivación para admisión"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Detectar duplicados
    tiene_duplicados, casos_duplicados = ServicioDeteccionDuplicados.detectar_duplicados(
        caso.ciudadano_titular
    )
    
    # Verificar SLA
    sla_vencido = ServicioSLA.esta_vencido(caso.sla_revision)
    
    context = {
        'caso': caso,
        'tiene_duplicados': tiene_duplicados,
        'casos_duplicados': casos_duplicados,
        'sla_vencido': sla_vencido,
    }
    
    return render(request, 'nachec/detalle_derivacion.html', context)


@login_required
@user_passes_test(es_operador)
@require_POST
def tomar_caso(request, caso_id):
    """Tomar caso (DERIVADO → EN_REVISION)"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    try:
        ServicioTransicionNachec.tomar_caso(caso, request.user)
        messages.success(request, f'Caso tomado exitosamente')
        return redirect('nachec:detalle_derivacion', caso_id=caso.id)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('nachec:bandeja_derivaciones')


@login_required
@user_passes_test(es_operador)
@require_POST
def rechazar_caso(request, caso_id):
    """Rechazar caso"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    motivo = request.POST.get('motivo', '')
    
    try:
        ServicioTransicionNachec.rechazar_caso(caso, request.user, motivo)
        messages.success(request, 'Caso rechazado')
        return redirect('nachec:bandeja_derivaciones')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('nachec:detalle_derivacion', caso_id=caso.id)


@login_required
@user_passes_test(es_operador)
@require_POST
def enviar_a_asignacion(request, caso_id):
    """Enviar caso a asignación (EN_REVISION → A_ASIGNAR)"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    try:
        ServicioTransicionNachec.enviar_a_asignacion(caso, request.user)
        messages.success(request, 'Caso enviado a asignación')
        return redirect('nachec:bandeja_derivaciones')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('nachec:detalle_derivacion', caso_id=caso.id)


# ============================================================================
# BANDEJA 2: PENDIENTES DE ASIGNACIÓN (Coordinador)
# ============================================================================

@login_required
@user_passes_test(es_coordinador)
def bandeja_asignacion(request):
    """Bandeja de casos pendientes de asignación"""
    
    # Filtros
    municipio = request.GET.get('municipio', '')
    prioridad = request.GET.get('prioridad', '')
    
    # Query
    casos = CasoNachec.objects.filter(
        estado=EstadoCaso.A_ASIGNAR
    ).select_related('ciudadano_titular')
    
    if municipio:
        casos = casos.filter(municipio=municipio)
    if prioridad:
        casos = casos.filter(prioridad=prioridad)
    
    # Paginación
    paginator = Paginator(casos, 20)
    page = request.GET.get('page', 1)
    casos_page = paginator.get_page(page)
    
    # Territoriales disponibles
    from django.contrib.auth.models import Group
    grupo_territorial = Group.objects.filter(name__in=['Territorial', 'Trabajador Territorial']).first()
    territoriales = grupo_territorial.user_set.all() if grupo_territorial else []
    
    context = {
        'casos': casos_page,
        'territoriales': territoriales,
        'total': casos.count(),
    }
    
    return render(request, 'nachec/bandeja_asignacion.html', context)


@login_required
@user_passes_test(es_coordinador)
@require_POST
def asignar_territorial(request, caso_id):
    """Asignar territorial a caso"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    territorial_id = request.POST.get('territorial_id')
    
    if not territorial_id:
        messages.error(request, 'Debe seleccionar un territorial')
        return redirect('nachec:bandeja_asignacion')
    
    from django.contrib.auth.models import User
    territorial = get_object_or_404(User, id=territorial_id)
    
    try:
        ServicioTransicionNachec.asignar_territorial(caso, request.user, territorial)
        messages.success(request, f'Caso asignado a {territorial.get_full_name()}')
        return redirect('nachec:bandeja_asignacion')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('nachec:bandeja_asignacion')


# ============================================================================
# BANDEJA 3: MIS CASOS (Territorial)
# ============================================================================

@login_required
@user_passes_test(es_territorial)
def mis_casos(request):
    """Bandeja de casos del territorial"""
    
    # Filtros por estado
    estado = request.GET.get('estado', '')
    
    # Query
    casos = CasoNachec.objects.filter(
        territorial=request.user
    ).exclude(
        estado__in=[EstadoCaso.CERRADO, EstadoCaso.RECHAZADO]
    ).select_related('ciudadano_titular')
    
    if estado:
        casos = casos.filter(estado=estado)
    
    # Agrupar por estado
    casos_asignados = casos.filter(estado=EstadoCaso.ASIGNADO)
    casos_relevamiento = casos.filter(estado=EstadoCaso.EN_RELEVAMIENTO)
    casos_seguimiento = casos.filter(estado=EstadoCaso.EN_SEGUIMIENTO)
    
    # Tareas pendientes
    tareas_pendientes = TareaNachec.objects.filter(
        asignado_a=request.user,
        estado='PENDIENTE'
    ).select_related('caso').order_by('fecha_vencimiento')[:10]
    
    context = {
        'casos_asignados': casos_asignados,
        'casos_relevamiento': casos_relevamiento,
        'casos_seguimiento': casos_seguimiento,
        'tareas_pendientes': tareas_pendientes,
        'total': casos.count(),
    }
    
    return render(request, 'nachec/mis_casos.html', context)


@login_required
@user_passes_test(es_territorial)
@require_POST
def iniciar_relevamiento(request, caso_id):
    """Iniciar relevamiento (ASIGNADO → EN_RELEVAMIENTO)"""
    caso = get_object_or_404(CasoNachec, id=caso_id, territorial=request.user)
    
    try:
        ServicioTransicionNachec.iniciar_relevamiento(caso, request.user)
        messages.success(request, 'Relevamiento iniciado')
        return redirect('nachec:formulario_relevamiento', caso_id=caso.id)
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('nachec:mis_casos')


@login_required
@user_passes_test(es_territorial)
def formulario_relevamiento(request, caso_id):
    """Formulario de relevamiento sociofamiliar"""
    caso = get_object_or_404(CasoNachec, id=caso_id, territorial=request.user)
    
    # Obtener o crear relevamiento
    relevamiento, created = RelevamientoNachec.objects.get_or_create(
        caso=caso,
        defaults={'territorial': request.user}
    )
    
    if request.method == 'POST':
        # Guardar datos del relevamiento
        relevamiento.cantidad_convivientes = request.POST.get('cantidad_convivientes', 0)
        relevamiento.hay_embarazo = request.POST.get('hay_embarazo') == 'on'
        relevamiento.hay_discapacidad = request.POST.get('hay_discapacidad') == 'on'
        relevamiento.detalle_discapacidad = request.POST.get('detalle_discapacidad', '')
        
        relevamiento.ingreso_mensual_rango = request.POST.get('ingreso_mensual_rango')
        relevamiento.fuente_ingreso = request.POST.get('fuente_ingreso')
        relevamiento.situacion_laboral = request.POST.get('situacion_laboral')
        
        relevamiento.tipo_vivienda = request.POST.get('tipo_vivienda')
        relevamiento.material_predominante = request.POST.get('material_predominante')
        relevamiento.tiene_agua = request.POST.get('tiene_agua') == 'on'
        relevamiento.tiene_luz = request.POST.get('tiene_luz') == 'on'
        relevamiento.tiene_gas = request.POST.get('tiene_gas') == 'on'
        relevamiento.tiene_cloaca = request.POST.get('tiene_cloaca') == 'on'
        
        relevamiento.cobertura_salud = request.POST.get('cobertura_salud')
        relevamiento.menores_escolarizados = request.POST.get('menores_escolarizados') == 'on'
        relevamiento.acceso_alimentos = request.POST.get('acceso_alimentos')
        relevamiento.frecuencia_comidas = request.POST.get('frecuencia_comidas', 0)
        
        relevamiento.hay_violencia = request.POST.get('hay_violencia') == 'on'
        relevamiento.hay_situacion_calle = request.POST.get('hay_situacion_calle') == 'on'
        relevamiento.urgencia_alimentaria = request.POST.get('urgencia_alimentaria') == 'on'
        
        # Marcar como completado si se solicita
        if request.POST.get('finalizar') == 'true':
            relevamiento.completado = True
            from django.utils import timezone
            relevamiento.fecha_finalizacion = timezone.now()
        
        relevamiento.save()
        
        if relevamiento.completado:
            try:
                ServicioTransicionNachec.finalizar_relevamiento(caso, request.user)
                messages.success(request, 'Relevamiento finalizado exitosamente')
                return redirect('nachec:mis_casos')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.success(request, 'Relevamiento guardado')
    
    context = {
        'caso': caso,
        'relevamiento': relevamiento,
    }
    
    return render(request, 'nachec/formulario_relevamiento.html', context)


# ============================================================================
# EVALUACIÓN (Evaluador)
# ============================================================================

@login_required
@user_passes_test(es_evaluador)
def bandeja_evaluacion(request):
    """Bandeja de casos para evaluar"""
    casos = CasoNachec.objects.filter(
        estado=EstadoCaso.EVALUADO
    ).select_related('ciudadano_titular', 'relevamiento')
    
    paginator = Paginator(casos, 20)
    page = request.GET.get('page', 1)
    casos_page = paginator.get_page(page)
    
    context = {
        'casos': casos_page,
        'total': casos.count(),
    }
    
    return render(request, 'nachec/bandeja_evaluacion.html', context)


@login_required
@user_passes_test(es_evaluador)
def formulario_evaluacion(request, caso_id):
    """Formulario de evaluación de vulnerabilidad"""
    caso = get_object_or_404(CasoNachec, id=caso_id, estado=EstadoCaso.EVALUADO)
    
    if not hasattr(caso, 'relevamiento'):
        messages.error(request, 'No existe relevamiento para este caso')
        return redirect('nachec:bandeja_evaluacion')
    
    # Obtener o crear evaluación
    evaluacion, created = EvaluacionVulnerabilidad.objects.get_or_create(
        caso=caso,
        defaults={
            'relevamiento': caso.relevamiento,
            'evaluador': request.user,
            'score_total': 0,
            'score_composicion_familiar': 0,
            'score_ingresos': 0,
            'score_vivienda': 0,
            'score_salud': 0,
            'score_educacion': 0,
            'score_alimentacion': 0,
            'score_riesgos': 0,
        }
    )
    
    if request.method == 'POST':
        # Guardar scores
        evaluacion.score_composicion_familiar = float(request.POST.get('score_composicion_familiar', 0))
        evaluacion.score_ingresos = float(request.POST.get('score_ingresos', 0))
        evaluacion.score_vivienda = float(request.POST.get('score_vivienda', 0))
        evaluacion.score_salud = float(request.POST.get('score_salud', 0))
        evaluacion.score_educacion = float(request.POST.get('score_educacion', 0))
        evaluacion.score_alimentacion = float(request.POST.get('score_alimentacion', 0))
        evaluacion.score_riesgos = float(request.POST.get('score_riesgos', 0))
        
        # Calcular score total
        evaluacion.score_total = (
            evaluacion.score_composicion_familiar +
            evaluacion.score_ingresos +
            evaluacion.score_vivienda +
            evaluacion.score_salud +
            evaluacion.score_educacion +
            evaluacion.score_alimentacion +
            evaluacion.score_riesgos
        ) / 7
        
        evaluacion.categoria_final = request.POST.get('categoria_final')
        evaluacion.dictamen = request.POST.get('dictamen', '')
        evaluacion.recomendaciones = request.POST.get('recomendaciones', '')
        evaluacion.save()
        
        if request.POST.get('confirmar') == 'true':
            try:
                ServicioTransicionNachec.confirmar_evaluacion(caso, request.user)
                messages.success(request, 'Evaluación confirmada')
                return redirect('nachec:bandeja_evaluacion')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.success(request, 'Evaluación guardada')
    
    context = {
        'caso': caso,
        'relevamiento': caso.relevamiento,
        'evaluacion': evaluacion,
    }
    
    return render(request, 'nachec/formulario_evaluacion.html', context)


# ============================================================================
# PLAN DE INTERVENCIÓN (Referente)
# ============================================================================

@login_required
@user_passes_test(es_referente)
def bandeja_planes(request):
    """Bandeja de casos para crear plan"""
    casos = CasoNachec.objects.filter(
        estado=EstadoCaso.PLAN_DEFINIDO
    ).select_related('ciudadano_titular', 'evaluacion')
    
    paginator = Paginator(casos, 20)
    page = request.GET.get('page', 1)
    casos_page = paginator.get_page(page)
    
    context = {
        'casos': casos_page,
        'total': casos.count(),
    }
    
    return render(request, 'nachec/bandeja_planes.html', context)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
def api_caso_detalle(request, caso_id):
    """API para obtener detalle de caso"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    data = {
        'id': caso.id,
        'ciudadano': caso.ciudadano_titular.nombre_completo,
        'estado': caso.get_estado_display(),
        'prioridad': caso.get_prioridad_display(),
        'municipio': caso.municipio,
        'localidad': caso.localidad,
        'tiene_duplicado': caso.tiene_duplicado,
    }
    
    return JsonResponse(data)
