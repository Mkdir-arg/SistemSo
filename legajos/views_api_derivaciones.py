"""
Vistas API para derivaciones de programas
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ciudadano
from .models_programas import DerivacionPrograma, Programa


@login_required
def derivaciones_programa_api(request, ciudadano_id, programa_id):
    """
    API para obtener derivaciones de un ciudadano a un programa específico
    """
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    programa = get_object_or_404(Programa, id=programa_id)
    
    # Obtener todas las derivaciones al programa (origen o destino)
    derivaciones = DerivacionPrograma.objects.filter(
        ciudadano=ciudadano,
        programa_destino=programa
    ).select_related(
        'programa_origen',
        'derivado_por',
        'respondido_por'
    ).order_by('-creado')
    
    derivaciones_data = []
    for derivacion in derivaciones:
        derivaciones_data.append({
            'id': derivacion.id,
            'creado': derivacion.creado.isoformat(),
            'programa_origen': derivacion.programa_origen.nombre if derivacion.programa_origen else None,
            'motivo': derivacion.motivo,
            'urgencia': derivacion.urgencia,
            'urgencia_display': derivacion.get_urgencia_display(),
            'estado': derivacion.estado,
            'estado_display': derivacion.get_estado_display(),
            'derivado_por': derivacion.derivado_por.get_full_name() if derivacion.derivado_por else None,
            'fecha_respuesta': derivacion.fecha_respuesta.isoformat() if derivacion.fecha_respuesta else None,
            'respondido_por': derivacion.respondido_por.get_full_name() if derivacion.respondido_por else None,
            'respuesta': derivacion.respuesta,
        })
    
    return JsonResponse({
        'success': True,
        'derivaciones': derivaciones_data,
        'total': len(derivaciones_data)
    })
