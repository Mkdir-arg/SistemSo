from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models_programas import DerivacionPrograma

@login_required
def aceptar_derivacion_programa(request, derivacion_id):
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)
    
    if derivacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
    
    try:
        inscripcion = derivacion.aceptar(usuario=request.user)
        messages.success(request, f'Derivación aceptada. {derivacion.ciudadano.nombre_completo} inscrito en {derivacion.programa_destino.nombre}.')
    except Exception as e:
        messages.error(request, f'Error al aceptar derivación: {str(e)}')
    
    return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)


@login_required
def rechazar_derivacion_programa(request, derivacion_id):
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)
    
    if derivacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
    
    try:
        derivacion.rechazar(usuario=request.user, motivo_rechazo='Rechazado desde bandeja de derivaciones')
        messages.success(request, f'Derivación de {derivacion.ciudadano.nombre_completo} rechazada.')
    except Exception as e:
        messages.error(request, f'Error al rechazar derivación: {str(e)}')
    
    return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
