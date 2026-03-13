from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models_programas import DerivacionPrograma
from django.http import JsonResponse

@login_required
def aceptar_derivacion_programa(request, derivacion_id):
    derivacion = get_object_or_404(DerivacionPrograma, id=derivacion_id)
    
    if derivacion.estado != 'PENDIENTE':
        messages.warning(request, 'Esta derivación ya fue procesada.')
        return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
    
    # Si es Ñachec, mostrar modal de validación
    if derivacion.programa_destino.tipo in ['NACHEC', 'ÑACHEC']:
        if request.method == 'GET':
            # Validar datos mínimos
            ciudadano = derivacion.ciudadano
            validaciones = {
                'tiene_nombre': bool(ciudadano.nombre and ciudadano.apellido),
                'tiene_dni': bool(ciudadano.dni),
                'tiene_contacto': bool(ciudadano.telefono or ciudadano.domicilio),
                'tiene_municipio': bool(ciudadano.municipio),
            }
            
            # Detectar duplicados por DNI
            from .models_nachec import CasoNachec
            duplicados = []
            if ciudadano.dni and ciudadano.dni.strip():
                duplicados = CasoNachec.objects.filter(
                    ciudadano_titular__dni=ciudadano.dni
                ).exclude(estado__in=['DERIVADO', 'CERRADO', 'RECHAZADO', 'SUSPENDIDO']).select_related('ciudadano_titular')
            
            return render(request, 'legajos/nachec/modal_aceptar_derivacion.html', {
                'derivacion': derivacion,
                'validaciones': validaciones,
                'duplicados': duplicados,
                'datos_completos': all(validaciones.values())
            })
        
        # POST: Procesar aceptación
        if request.method == 'POST':
            # Validación de concurrencia
            derivacion.refresh_from_db()
            if derivacion.estado != 'PENDIENTE':
                messages.error(request, 'Esta derivación ya fue procesada por otro usuario')
                return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
            
            # Validar duplicados
            if request.POST.get('tiene_duplicado') == 'true':
                resolucion = request.POST.get('resolucion_duplicado')
                
                if resolucion == 'vincular':
                    messages.info(request, 'Funcionalidad de vincular a caso existente en desarrollo')
                    return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
                
                elif resolucion == 'justificar':
                    justificacion = request.POST.get('justificacion_duplicado', '').strip()
                    if not justificacion:
                        messages.error(request, 'Debe justificar la creación de nuevo caso')
                        return redirect('legajos:derivacion_aceptar', derivacion_id=derivacion_id)
                
                else:
                    messages.error(request, 'Debe seleccionar una opción para resolver el duplicado')
                    return redirect('legajos:derivacion_aceptar', derivacion_id=derivacion_id)
            
            try:
                # Aceptar derivación
                inscripcion = derivacion.aceptar(usuario=request.user)
                
                # Crear tarea automática con SLA
                from .models_nachec import CasoNachec, TareaNachec
                from datetime import timedelta
                from django.utils import timezone
                
                caso = CasoNachec.objects.filter(ciudadano_titular=derivacion.ciudadano).first()
                if caso:
                    # Calcular SLA según urgencia
                    urgencia = request.POST.get('urgencia', 'MEDIA')
                    sla_dias = {'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(urgencia, 2)
                    
                    # Actualizar prioridad del caso
                    caso.prioridad = urgencia
                    caso.save()
                    
                    # Crear tarea de revisión inicial
                    TareaNachec.objects.create(
                        caso=caso,
                        tipo='VALIDACION',
                        titulo='Revisión inicial - Validación de datos',
                        descripcion=f"""Checklist de revisión inicial:
- Validar identidad (DNI o documento alternativo)
- Validar jurisdicción (municipio/localidad)
- Verificar datos de contacto
- Determinar si corresponde relevamiento territorial
- Definir si requiere asistencia inmediata
- Confirmar o ajustar prioridad
- Determinar próximos pasos

Tipo de atención: {request.POST.get('tipo_atencion', 'No especificado')}
Comentario: {request.POST.get('comentario', 'Sin comentarios')}""",
                        asignado_a=request.user,
                        creado_por=request.user,
                        estado='PENDIENTE',
                        prioridad=urgencia,
                        fecha_vencimiento=timezone.now().date() + timedelta(days=sla_dias)
                    )
                    
                    # Auditoría
                    from .models_nachec import HistorialEstadoCaso
                    HistorialEstadoCaso.objects.create(
                        caso=caso,
                        estado_anterior='DERIVADO',
                        estado_nuevo=caso.estado,
                        usuario=request.user,
                        observacion=f"Derivación aceptada. SLA: {sla_dias} días. Urgencia: {urgencia}"
                    )
                
                messages.success(request, f'Derivación aceptada. Caso en revisión con tarea asignada.')
            except Exception as e:
                messages.error(request, f'Error al aceptar derivación: {str(e)}')
            
            return redirect('legajos:programa_detalle', pk=derivacion.programa_destino.id)
    
    # Flujo normal para otros programas
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
