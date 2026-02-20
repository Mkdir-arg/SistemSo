"""
Vistas para Sistema NODO - Gestión Programática Institucional
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.core.exceptions import ValidationError

from core.models import Institucion
from .models import LegajoInstitucional
from .models_institucional import (
    InstitucionPrograma,
    DerivacionInstitucional,
    CasoInstitucional,
    EstadoDerivacion,
    EstadoCaso,
    EstadoPrograma
)
from .forms_institucional import (
    DerivacionInstitucionalForm,
    RechazarDerivacionForm,
    CambiarEstadoCasoForm
)
from .services_institucional import DerivacionService, CasoService
from .permissions_institucional import (
    puede_ver_institucion,
    puede_ver_programa,
    puede_operar_programa,
    require_ver_institucion,
    require_operar_programa
)


@login_required
@require_ver_institucion
def institucion_detalle_programatico(request, pk):
    """
    Vista principal de detalle institucional con solapas dinámicas por programa.
    Genera solapas estáticas + dinámicas según programas activos.
    """
    institucion = get_object_or_404(Institucion, pk=pk)
    
    # Obtener o crear legajo institucional
    legajo, created = LegajoInstitucional.objects.get_or_create(
        institucion=institucion,
        defaults={'responsable_sedronar': request.user}
    )
    
    # Solapas estáticas
    solapas = [
        {'id': 'resumen', 'nombre': 'Resumen', 'icono': 'dashboard', 'orden': 1, 'tipo': 'estatica'},
        {'id': 'personal', 'nombre': 'Personal', 'icono': 'people', 'orden': 2, 'tipo': 'estatica'},
        {'id': 'evaluaciones', 'nombre': 'Evaluaciones', 'icono': 'assessment', 'orden': 3, 'tipo': 'estatica'},
        {'id': 'documentos', 'nombre': 'Documentos', 'icono': 'folder', 'orden': 4, 'tipo': 'estatica'},
    ]
    
    # Solapas dinámicas (programas activos con anotaciones optimizadas)
    programas_activos = InstitucionPrograma.objects.filter(
        institucion=institucion,
        activo=True,
        estado_programa=EstadoPrograma.ACTIVO
    ).select_related('programa').annotate(
        derivaciones_pendientes=Count(
            'derivaciones',
            filter=Q(derivaciones__estado=EstadoDerivacion.PENDIENTE)
        ),
        casos_activos=Count(
            'casos',
            filter=Q(casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])
        )
    ).order_by('programa__orden')
    
    for ip in programas_activos:
        # Verificar si el usuario puede ver este programa
        if puede_ver_programa(ip, request.user):
            solapas.append({
                'id': f'programa_{ip.programa.id}',
                'nombre': ip.programa.nombre,
                'icono': ip.programa.icono,
                'color': ip.programa.color,
                'orden': 100 + ip.programa.orden,
                'tipo': 'programa',
                'badge_derivaciones': ip.derivaciones_pendientes,
                'badge_casos': ip.casos_activos,
                'institucion_programa_id': ip.id,
                'puede_operar': puede_operar_programa(ip, request.user)
            })
    
    # Ordenar solapas
    solapas = sorted(solapas, key=lambda x: x['orden'])
    
    # Métricas consolidadas para resumen
    total_derivaciones_pendientes = sum(s.get('badge_derivaciones', 0) for s in solapas if s['tipo'] == 'programa')
    total_casos_activos = sum(s.get('badge_casos', 0) for s in solapas if s['tipo'] == 'programa')
    total_programas_activos = len([s for s in solapas if s['tipo'] == 'programa'])
    
    context = {
        'institucion': institucion,
        'legajo': legajo,
        'solapas': solapas,
        'total_derivaciones_pendientes': total_derivaciones_pendientes,
        'total_casos_activos': total_casos_activos,
        'total_programas_activos': total_programas_activos,
    }
    
    return render(request, 'configuracion/institucion_detail.html', context)


@login_required
@require_operar_programa
def programa_derivaciones(request, institucion_programa_id):
    """Vista de derivaciones de un programa específico"""
    ip = request.institucion_programa
    
    # Filtros
    estado = request.GET.get('estado', '')
    
    derivaciones = DerivacionInstitucional.objects.filter(
        institucion_programa=ip
    ).select_related('ciudadano', 'derivado_por')
    
    if estado:
        derivaciones = derivaciones.filter(estado=estado)
    
    derivaciones = derivaciones.order_by('-creado')
    
    context = {
        'institucion_programa': ip,
        'derivaciones': derivaciones,
        'estados': EstadoDerivacion.choices,
        'estado_filtro': estado,
    }
    
    return render(request, 'legajos/programa_derivaciones.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def aceptar_derivacion(request, derivacion_id):
    """Acepta una derivación institucional"""
    derivacion = get_object_or_404(DerivacionInstitucional, id=derivacion_id)
    
    # Verificar permisos
    if not puede_operar_programa(derivacion.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para operar este programa.')
        return redirect('legajos:programas')
    
    try:
        caso, created = DerivacionService.aceptar_derivacion(
            derivacion_id=derivacion_id,
            usuario=request.user
        )
        
        if created:
            messages.success(request, f'Derivación aceptada. Caso {caso.codigo} creado exitosamente.')
        else:
            messages.info(request, f'Derivación unificada con caso existente {caso.codigo}.')
        
        return redirect('legajos:programa_casos', institucion_programa_id=caso.institucion_programa.id)
        
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_http_methods(["GET", "POST"])
def rechazar_derivacion_view(request, derivacion_id):
    """Vista para rechazar derivación"""
    derivacion = get_object_or_404(DerivacionInstitucional, id=derivacion_id)
    
    # Verificar permisos
    if not puede_operar_programa(derivacion.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para operar este programa.')
        return redirect('legajos:programas')
    
    if request.method == 'POST':
        form = RechazarDerivacionForm(request.POST)
        if form.is_valid():
            try:
                DerivacionService.rechazar_derivacion(
                    derivacion_id=derivacion_id,
                    usuario=request.user,
                    motivo_rechazo=form.cleaned_data['motivo_rechazo']
                )
                messages.success(request, 'Derivación rechazada exitosamente.')
                return redirect('legajos:programa_derivaciones', 
                              institucion_programa_id=derivacion.institucion_programa.id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = RechazarDerivacionForm()
    
    context = {
        'derivacion': derivacion,
        'form': form,
    }
    
    return render(request, 'legajos/rechazar_derivacion.html', context)


@login_required
@require_operar_programa
def programa_casos(request, institucion_programa_id):
    """Vista de casos activos de un programa"""
    ip = request.institucion_programa
    
    # Filtros
    estado = request.GET.get('estado', '')
    
    casos = CasoInstitucional.objects.filter(
        institucion_programa=ip
    ).select_related('ciudadano', 'responsable_caso')
    
    if estado:
        casos = casos.filter(estado=estado)
    else:
        # Por defecto mostrar solo activos y en seguimiento
        casos = casos.filter(estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])
    
    casos = casos.order_by('-fecha_apertura')
    
    context = {
        'institucion_programa': ip,
        'casos': casos,
        'estados': EstadoCaso.choices,
        'estado_filtro': estado,
    }
    
    return render(request, 'legajos/programa_casos.html', context)


@login_required
def caso_detalle(request, caso_id):
    """Detalle de un caso institucional"""
    caso = get_object_or_404(
        CasoInstitucional.objects.select_related(
            'ciudadano',
            'institucion_programa__institucion',
            'institucion_programa__programa',
            'responsable_caso',
            'derivacion_origen'
        ),
        id=caso_id
    )
    
    # Verificar permisos
    if not puede_ver_programa(caso.institucion_programa, request.user):
        messages.error(request, 'No tiene permisos para ver este caso.')
        return redirect('legajos:ciudadanos')
    
    # TODO: Historial de estados cuando exista HistorialEstadoCaso
    # historial = caso.historial_estados.select_related('usuario').order_by('-creado')
    historial = []
    
    context = {
        'caso': caso,
        'historial': historial,
        'puede_operar': puede_operar_programa(caso.institucion_programa, request.user),
    }
    
    return render(request, 'legajos/caso_detalle.html', context)


@login_required
@require_operar_programa
def cambiar_estado_caso_view(request, caso_id):
    """Vista para cambiar estado de caso"""
    caso = get_object_or_404(CasoInstitucional, id=caso_id)
    
    if request.method == 'POST':
        form = CambiarEstadoCasoForm(request.POST)
        if form.is_valid():
            try:
                CasoService.cambiar_estado_caso(
                    caso_id=caso_id,
                    nuevo_estado=form.cleaned_data['nuevo_estado'],
                    usuario=request.user,
                    observacion=form.cleaned_data.get('observacion', ''),
                    motivo_cierre=form.cleaned_data.get('motivo_cierre', '')
                )
                messages.success(request, 'Estado del caso actualizado exitosamente.')
                return redirect('legajos:caso_detalle', caso_id=caso_id)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CambiarEstadoCasoForm(initial={'nuevo_estado': caso.estado})
    
    context = {
        'caso': caso,
        'form': form,
    }
    
    return render(request, 'legajos/cambiar_estado_caso.html', context)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_programa_indicadores(request, institucion_programa_id):
    """API: Indicadores de un programa"""
    ip = get_object_or_404(InstitucionPrograma, id=institucion_programa_id)
    
    if not puede_ver_programa(ip, request.user):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    # Calcular indicadores
    total_derivaciones = ip.derivaciones.count()
    derivaciones_pendientes = ip.derivaciones.filter(estado=EstadoDerivacion.PENDIENTE).count()
    derivaciones_aceptadas = ip.derivaciones.filter(estado=EstadoDerivacion.ACEPTADA).count()
    
    total_casos = ip.casos.count()
    casos_activos = ip.casos.filter(estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]).count()
    casos_egresados = ip.casos.filter(estado=EstadoCaso.EGRESADO).count()
    
    cupo_utilizado = casos_activos
    cupo_disponible = ip.cupo_disponible
    
    data = {
        'total_derivaciones': total_derivaciones,
        'derivaciones_pendientes': derivaciones_pendientes,
        'derivaciones_aceptadas': derivaciones_aceptadas,
        'total_casos': total_casos,
        'casos_activos': casos_activos,
        'casos_egresados': casos_egresados,
        'cupo_utilizado': cupo_utilizado,
        'cupo_maximo': ip.cupo_maximo,
        'cupo_disponible': cupo_disponible,
        'controla_cupo': ip.controlar_cupo,
    }
    
    return JsonResponse(data)
