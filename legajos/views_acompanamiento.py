from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models_programas import Programa, InscripcionPrograma
from .models import Ciudadano

@login_required
def crear_legajo_acompanamiento(request, inscripcion_id):
    """Crea el legajo para un acompañamiento existente"""
    inscripcion = get_object_or_404(InscripcionPrograma, pk=inscripcion_id)
    
    # Verificar si ya tiene legajo
    if inscripcion.legajo_id:
        messages.info(request, 'Este acompañamiento ya tiene un legajo creado.')
        return redirect('legajos:detalle', pk=inscripcion.legajo_id)
    
    # Guardar ciudadano en sesión para el flujo de admisión
    request.session['admision_ciudadano_id'] = inscripcion.ciudadano.id
    request.session['inscripcion_programa_id'] = inscripcion.id
    
    return redirect('legajos:admision_paso2')
