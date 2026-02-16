"""
Vistas para gestionar derivaciones de programas (aceptar/rechazar)
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models_programas import DerivacionPrograma


@login_required
def aceptar_derivacion_view(request, derivacion_id):
    """Acepta una derivación y redirige según el programa"""
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)
    
    try:
        # Aceptar la derivación
        inscripcion = derivacion.aceptar(usuario=request.user)
        
        messages.success(request, f'Derivación aceptada. Inscripción creada para {derivacion.programa_destino.nombre}')
        
        # Si es SEDRONAR, redirigir al paso 2 de admisión
        if derivacion.programa_destino.tipo == 'ACOMPANAMIENTO_SEDRONAR':
            # Guardar ciudadano en sesión para el flujo de admisión
            request.session['admision_ciudadano_id'] = derivacion.ciudadano.id
            return redirect('legajos:admision_paso2')
        
        # Para otros programas, redirigir al detalle del ciudadano
        return redirect('legajos:ciudadano_detalle', pk=derivacion.ciudadano.id)
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('legajos:bandeja_derivaciones')


@login_required
def rechazar_derivacion_view(request, derivacion_id):
    """Rechaza una derivación"""
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo_rechazo', '')
        
        if not motivo:
            messages.error(request, 'Debe proporcionar un motivo de rechazo')
            return redirect('legajos:bandeja_derivaciones')
        
        try:
            derivacion.rechazar(usuario=request.user, motivo_rechazo=motivo)
            messages.warning(request, f'Derivación rechazada: {derivacion.programa_destino.nombre}')
        except ValueError as e:
            messages.error(request, str(e))
        
        return redirect('legajos:bandeja_derivaciones')
    
    return redirect('legajos:bandeja_derivaciones')
