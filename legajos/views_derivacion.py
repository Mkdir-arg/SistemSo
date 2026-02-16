from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ciudadano
from .models_programas import DerivacionPrograma
from .forms_derivacion import DerivarProgramaForm
from .services_solapas import SolapasService


@login_required
def derivar_programa_view(request, ciudadano_id):
    """Vista para derivar ciudadano a un programa"""
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    
    # Obtener programas activos y disponibles
    programas_activos = SolapasService.obtener_programas_activos(ciudadano)
    programas_disponibles = SolapasService.obtener_programas_disponibles_derivacion(ciudadano)
    
    if not programas_disponibles.exists():
        messages.warning(request, 'El ciudadano ya está inscrito en todos los programas disponibles.')
        return redirect('legajos:ciudadano_detalle', pk=ciudadano_id)
    
    if request.method == 'POST':
        form = DerivarProgramaForm(request.POST, ciudadano=ciudadano)
        if form.is_valid():
            derivacion = form.save(commit=False)
            derivacion.ciudadano = ciudadano
            derivacion.derivado_por = request.user
            
            # Si hay programa origen, obtener la inscripción
            if derivacion.programa_origen:
                inscripcion_origen = programas_activos.filter(
                    programa=derivacion.programa_origen
                ).first()
                if inscripcion_origen:
                    derivacion.inscripcion_origen = inscripcion_origen
            
            derivacion.save()
            
            messages.success(
                request,
                f'Derivación creada exitosamente a {derivacion.programa_destino.nombre}. '
                f'Estado: Pendiente de aceptación.'
            )
            return redirect('legajos:ciudadano_detalle', pk=ciudadano_id)
    else:
        form = DerivarProgramaForm(ciudadano=ciudadano)
    
    context = {
        'ciudadano': ciudadano,
        'form': form,
        'programas_activos': programas_activos,
        'programas_disponibles': programas_disponibles,
    }
    
    return render(request, 'legajos/derivar_programa.html', context)
