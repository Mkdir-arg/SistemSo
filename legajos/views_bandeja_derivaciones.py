"""
Vista de bandeja de derivaciones de programas
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models_programas import DerivacionPrograma, Programa


@login_required
def bandeja_derivaciones_view(request):
    """
    Bandeja de derivaciones de programas
    Muestra derivaciones pendientes agrupadas por programa
    """
    # Filtros
    programa_id = request.GET.get('programa')
    estado = request.GET.get('estado', 'PENDIENTE')
    
    # Query base
    derivaciones = DerivacionPrograma.objects.select_related(
        'ciudadano',
        'programa_origen',
        'programa_destino',
        'derivado_por',
        'respondido_por'
    ).order_by('-creado')
    
    # Aplicar filtros
    if estado:
        derivaciones = derivaciones.filter(estado=estado)
    
    if programa_id:
        derivaciones = derivaciones.filter(programa_destino_id=programa_id)
    
    # Obtener programas para el filtro
    programas = Programa.objects.filter(activo=True).order_by('nombre')
    
    # Estadísticas
    stats = {
        'pendientes': DerivacionPrograma.objects.filter(estado='PENDIENTE').count(),
        'aceptadas': DerivacionPrograma.objects.filter(estado='ACEPTADA').count(),
        'rechazadas': DerivacionPrograma.objects.filter(estado='RECHAZADA').count(),
        'total': DerivacionPrograma.objects.count(),
    }
    
    context = {
        'derivaciones': derivaciones,
        'programas': programas,
        'stats': stats,
        'estado_actual': estado,
        'programa_actual': int(programa_id) if programa_id else None,
    }
    
    return render(request, 'legajos/bandeja_derivaciones.html', context)
