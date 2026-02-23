"""
Vistas para transiciones de estado en Ñachec
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from .models_nachec import CasoNachec, HistorialEstadoCaso, RelevamientoNachec, TareaNachec


def _get_municipios():
    """Obtener lista de municipios"""
    from core.models import Municipio
    return Municipio.objects.all().order_by('nombre')


@login_required
def completar_validacion(request, caso_id):
    """Completar validación creando tarea si no existe"""
    from .models_nachec import TareaNachec
    from django.utils import timezone
    from datetime import timedelta
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if request.method == 'POST':
        # Buscar o crear tarea
        tarea, created = TareaNachec.objects.get_or_create(
            caso=caso,
            tipo='VALIDACION',
            defaults={
                'titulo': 'Revisión inicial - Validación de datos',
                'descripcion': 'Checklist de revisión inicial completado',
                'asignado_a': request.user,
                'creado_por': request.user,
                'estado': 'COMPLETADA',
                'prioridad': caso.prioridad or 'MEDIA',
                'fecha_vencimiento': timezone.now().date() + timedelta(days=2)
            }
        )
        
        if not created:
            tarea.estado = 'COMPLETADA'
            tarea.save()
        
        messages.success(request, 'Validación completada. Ahora puede enviar el caso a asignación.')
        return redirect('legajos:programa_detalle', pk=2)
    
    return redirect('legajos:nachec_ver_tarea_validacion', caso_id=caso_id)


@login_required
def ver_tarea_validacion(request, caso_id):
    """Ver tarea de validación con checklist"""
    from .models_nachec import TareaNachec
    from django.shortcuts import render
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    tarea = TareaNachec.objects.filter(caso=caso, tipo='VALIDACION').first()
    
    return render(request, 'legajos/nachec/ver_tarea_validacion.html', {
        'caso': caso,
        'tarea': tarea
    })


@login_required
def completar_tarea(request, tarea_id):
    """Completar una tarea"""
    from .models_nachec import TareaNachec
    
    tarea = get_object_or_404(TareaNachec, id=tarea_id)
    
    if request.method == 'POST':
        tarea.estado = 'COMPLETADA'
        tarea.save()
        messages.success(request, f'Tarea "{tarea.titulo}" completada')
        return redirect(request.META.get('HTTP_REFERER', 'legajos:programa_detalle'), pk=2)
    
    return redirect('legajos:programa_detalle', pk=2)


@login_required
def enviar_a_asignacion(request, caso_id):
    """EN_REVISION → A_ASIGNAR con validación completa"""
    from .models_nachec import TareaNachec
    from django.shortcuts import render
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if caso.estado != 'EN_REVISION':
        messages.error(request, 'El caso no está en revisión')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        # Validaciones para el modal
        validaciones = {}
        
        # 1. Validar tarea VALIDACION completada
        tarea_validacion = TareaNachec.objects.filter(
            caso=caso,
            tipo='VALIDACION'
        ).first()
        validaciones['tarea_completada'] = tarea_validacion and tarea_validacion.estado == 'COMPLETADA'
        
        # 2. Validar DNI
        validaciones['tiene_dni'] = bool(caso.ciudadano_titular.dni)
        
        # 3. Validar prioridad
        validaciones['tiene_prioridad'] = bool(caso.prioridad)
        
        # 4. Validar municipio (BLOQUEANTE)
        validaciones['tiene_municipio'] = bool(caso.ciudadano_titular.municipio)
        
        # 5. Validar localidad
        validaciones['tiene_localidad'] = bool(caso.localidad and caso.localidad != 'Sin especificar')
        
        # Determinar si puede confirmar
        puede_confirmar = all([
            validaciones['tarea_completada'],
            validaciones['tiene_dni'],
            validaciones['tiene_prioridad'],
            validaciones['tiene_municipio']
        ])
        
        return render(request, 'legajos/nachec/modal_enviar_asignacion.html', {
            'caso': caso,
            'validaciones': validaciones,
            'puede_confirmar': puede_confirmar,
            'tarea_validacion': tarea_validacion,
            'municipios': _get_municipios()
        })
    
    # POST: Procesar envío
    if request.method == 'POST':
        # Validación de concurrencia
        caso.refresh_from_db()
        if caso.estado != 'EN_REVISION':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validaciones duras
        tarea_validacion = TareaNachec.objects.filter(
            caso=caso,
            tipo='VALIDACION',
            estado='COMPLETADA'
        ).first()
        
        if not tarea_validacion:
            messages.error(request, 'No se puede enviar: la tarea de validación no está completada')
            return redirect('legajos:nachec_enviar_asignacion', caso_id=caso_id)
        
        if not caso.ciudadano_titular.dni:
            messages.error(request, 'No se puede enviar: falta DNI del titular')
            return redirect('legajos:nachec_enviar_asignacion', caso_id=caso_id)
        
        if not caso.ciudadano_titular.municipio:
            messages.error(request, 'No se puede enviar: debe especificar municipio del ciudadano para asignación territorial')
            return redirect('legajos:nachec_enviar_asignacion', caso_id=caso_id)
        
        # Actualizar datos territoriales si vienen del form
        municipio = request.POST.get('municipio')
        localidad = request.POST.get('localidad')
        observaciones = request.POST.get('observaciones', '')
        
        if municipio:
            caso.municipio = municipio
        if localidad:
            caso.localidad = localidad
        
        # Cambiar estado
        from django.utils import timezone
        from datetime import timedelta
        
        estado_anterior = caso.estado
        caso.estado = 'A_ASIGNAR'
        caso.fecha_envio_asignacion = timezone.now()
        
        # Calcular SLA de asignación
        sla_horas = {'URGENTE': 12, 'ALTA': 12, 'MEDIA': 24, 'BAJA': 48}.get(caso.prioridad, 24)
        caso.sla_asignacion_hasta = timezone.now() + timedelta(hours=sla_horas)
        
        caso.save()
        
        # Crear tarea para coordinador
        TareaNachec.objects.create(
            caso=caso,
            tipo='OTRO',
            titulo='Asignar territorial al caso',
            descripcion=f"""Caso enviado a asignación territorial.

Municipio: {caso.municipio}
Localidad: {caso.localidad}
Prioridad: {caso.get_prioridad_display()}

Observaciones del operador:
{observaciones}

Debe asignar un territorial de la zona para iniciar relevamiento.""",
            asignado_a=request.user,  # TODO: asignar a coordinador por municipio
            creado_por=request.user,
            estado='PENDIENTE',
            prioridad=caso.prioridad,
            fecha_vencimiento=(timezone.now() + timedelta(hours=sla_horas)).date()
        )
        
        # Auditoría completa
        HistorialEstadoCaso.objects.create(
            caso=caso,
            estado_anterior=estado_anterior,
            estado_nuevo=caso.estado,
            usuario=request.user,
            observacion=f"""Caso enviado a asignación territorial.
SLA: {sla_horas}h
Municipio: {caso.municipio}
Localidad: {caso.localidad}
Observaciones: {observaciones}"""
        )
        
        messages.success(request, f'Caso enviado a asignación. Tarea creada para Coordinación (SLA: {sla_horas}h)')
        return redirect('legajos:programa_detalle', pk=2)


@login_required
@login_required
def asignar_territorial(request, caso_id):
    """A_ASIGNAR → ASIGNADO con modal mejorado"""
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    from django.db import transaction
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if request.method == 'POST':
        # Validación de concurrencia
        caso.refresh_from_db()
        if caso.estado != 'A_ASIGNAR':
            messages.error(request, 'El caso ya fue asignado por otro usuario. Actualice la pantalla.')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validar campos obligatorios
        territorial_id = request.POST.get('territorial_id')
        fecha_limite = request.POST.get('fecha_limite_relevamiento')
        instrucciones = request.POST.get('instrucciones', '').strip()
        
        if not territorial_id:
            messages.error(request, 'Debe seleccionar un territorial válido')
            return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        
        if not fecha_limite:
            messages.error(request, 'Debe especificar fecha límite de relevamiento')
            return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        
        if len(instrucciones) < 10:
            messages.error(request, 'Las instrucciones deben tener al menos 10 caracteres')
            return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        
        # Validar territorial
        try:
            territorial = User.objects.get(id=territorial_id, is_active=True)
        except User.DoesNotExist:
            messages.error(request, 'El territorial seleccionado no es válido')
            return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        
        # Validar fecha límite
        from datetime import datetime
        try:
            fecha_limite_obj = datetime.strptime(fecha_limite, '%Y-%m-%d').date()
            if fecha_limite_obj < timezone.now().date():
                messages.error(request, 'La fecha límite no puede ser anterior a hoy')
                return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        except ValueError:
            messages.error(request, 'Formato de fecha inválido')
            return redirect('legajos:nachec_asignar_territorial', caso_id=caso.id)
        
        # Transacción atómica
        with transaction.atomic():
            # 1. Actualizar caso
            estado_anterior = caso.estado
            caso.estado = 'ASIGNADO'
            caso.territorial = territorial
            caso.coordinador = request.user
            caso.fecha_asignacion = timezone.now().date()
            caso.sla_relevamiento = fecha_limite_obj
            caso.instrucciones_asignacion = instrucciones
            caso.save()
            
            # 2. Cerrar tarea ASIGNACION
            tarea_asignacion = TareaNachec.objects.filter(
                caso=caso,
                tipo='ASIGNACION',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea_asignacion:
                tarea_asignacion.estado = 'COMPLETADA'
                tarea_asignacion.fecha_completada = timezone.now()
                tarea_asignacion.resultado = f"Asignado a {territorial.get_full_name()}. SLA relevamiento: {fecha_limite_obj.strftime('%d/%m/%Y')}"
                tarea_asignacion.save()
            
            # 3. Crear tarea RELEVAMIENTO (idempotente)
            tarea_relevamiento = TareaNachec.objects.filter(
                caso=caso,
                tipo='RELEVAMIENTO',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea_relevamiento:
                # Actualizar tarea existente
                tarea_relevamiento.asignado_a = territorial
                tarea_relevamiento.fecha_vencimiento = fecha_limite_obj
                tarea_relevamiento.descripcion = f"""Realizar relevamiento sociofamiliar del caso.

Instrucciones del coordinador:
{instrucciones}

Datos del caso:
- Ciudadano: {caso.ciudadano_titular.nombre_completo}
- DNI: {caso.ciudadano_titular.dni}
- Municipio: {caso.municipio}
- Localidad: {caso.localidad}
- Dirección: {caso.direccion}
- Prioridad: {caso.get_prioridad_display()}

Fecha límite: {fecha_limite_obj.strftime('%d/%m/%Y')}"""
                tarea_relevamiento.save()
            else:
                # Crear nueva tarea
                TareaNachec.objects.create(
                    caso=caso,
                    tipo='RELEVAMIENTO',
                    titulo='Relevamiento inicial del caso',
                    descripcion=f"""Realizar relevamiento sociofamiliar del caso.

Instrucciones del coordinador:
{instrucciones}

Datos del caso:
- Ciudadano: {caso.ciudadano_titular.nombre_completo}
- DNI: {caso.ciudadano_titular.dni}
- Municipio: {caso.municipio}
- Localidad: {caso.localidad}
- Dirección: {caso.direccion}
- Prioridad: {caso.get_prioridad_display()}

Fecha límite: {fecha_limite_obj.strftime('%d/%m/%Y')}""",
                    asignado_a=territorial,
                    creado_por=request.user,
                    estado='PENDIENTE',
                    prioridad=caso.prioridad,
                    fecha_vencimiento=fecha_limite_obj
                )
            
            # 4. Auditoría
            sla_cumplido = timezone.now().date() <= (caso.sla_revision or timezone.now().date())
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Territorial asignado: {territorial.get_full_name()}
SLA relevamiento: {fecha_limite_obj.strftime('%d/%m/%Y')}
SLA asignación cumplido: {'Sí' if sla_cumplido else 'No'}
Instrucciones: {instrucciones[:100]}..."""
            )
        
        messages.success(request, f'Territorial asignado exitosamente. Tarea de relevamiento creada con vencimiento {fecha_limite_obj.strftime("%d/%m/%Y")}.')
        return redirect('legajos:programa_detalle', pk=2)
    
    # GET: Mostrar modal
    # Calcular SLA asignación
    if caso.sla_revision:
        dias_restantes = (caso.sla_revision - timezone.now().date()).days
        if dias_restantes < 0:
            sla_texto = f"Vencido hace {abs(dias_restantes)} días"
        elif dias_restantes == 0:
            sla_texto = "Vence hoy"
        else:
            sla_texto = f"Vence en {dias_restantes} días"
    else:
        sla_texto = "No definido"
    
    # Calcular fecha límite por defecto según prioridad
    if caso.prioridad == 'URGENTE' or caso.prioridad == 'ALTA':
        dias_sla = 1
    elif caso.prioridad == 'MEDIA':
        dias_sla = 2
    else:
        dias_sla = 3
    
    fecha_limite_default = (timezone.now() + timedelta(days=dias_sla)).date()
    
    # Obtener territoriales con carga de trabajo
    territoriales = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
    for t in territoriales:
        t.casos_activos = CasoNachec.objects.filter(
            territorial=t,
            estado__in=['ASIGNADO', 'EN_RELEVAMIENTO', 'EN_EJECUCION', 'EN_SEGUIMIENTO']
        ).count()
    
    # Sugerir territoriales con menor carga
    territoriales_sugeridos = sorted(territoriales, key=lambda x: x.casos_activos)[:3]
    
    return render(request, 'legajos/nachec/modal_asignar_territorial.html', {
        'caso': caso,
        'territoriales': territoriales,
        'territoriales_sugeridos': territoriales_sugeridos,
        'sla_asignacion_texto': sla_texto,
        'fecha_limite_default': fecha_limite_default.strftime('%Y-%m-%d'),
        'fecha_minima': timezone.now().date().strftime('%Y-%m-%d')
    })


@login_required
def iniciar_relevamiento(request, caso_id):
    """ASIGNADO → EN_RELEVAMIENTO con control de acceso y validaciones"""
    from django.utils import timezone
    from django.db import transaction
    from django.http import HttpResponseForbidden
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if request.method == 'POST':
        # Validación 1: Estado debe ser ASIGNADO
        caso.refresh_from_db()
        if caso.estado != 'ASIGNADO':
            messages.error(request, 'El caso no está en estado ASIGNADO')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validación 2: Control de acceso - solo territorial asignado
        if request.user.id != caso.territorial_id:
            messages.error(request, 'No estás asignado como territorial a este caso')
            return HttpResponseForbidden('Acceso denegado: no eres el territorial asignado')
        
        # Validación 3: Debe existir tarea RELEVAMIENTO
        tarea_relevamiento = TareaNachec.objects.filter(
            caso=caso,
            tipo='RELEVAMIENTO',
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).first()
        
        if not tarea_relevamiento:
            messages.error(request, 'No existe tarea de relevamiento para este caso. Contactar coordinación.')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validación 4: Verificar SLA (no bloquea, solo registra)
        sla_vencido = False
        if caso.sla_relevamiento and timezone.now().date() > caso.sla_relevamiento:
            sla_vencido = True
        
        # Transacción atómica
        with transaction.atomic():
            # 1. Cambiar estado y registrar fecha inicio
            estado_anterior = caso.estado
            caso.estado = 'EN_RELEVAMIENTO'
            caso.fecha_inicio_relevamiento = timezone.now()
            caso.save()
            
            # 2. Actualizar tarea RELEVAMIENTO a EN_PROCESO
            if tarea_relevamiento.estado == 'PENDIENTE':
                tarea_relevamiento.estado = 'EN_PROCESO'
                tarea_relevamiento.save()
            
            # 3. Auditoría enriquecida
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Relevamiento iniciado por {request.user.get_full_name()}
SLA relevamiento: {caso.sla_relevamiento.strftime('%d/%m/%Y') if caso.sla_relevamiento else 'No definido'}
Inicio fuera de SLA: {'Sí' if sla_vencido else 'No'}
Tarea ID: {tarea_relevamiento.id}
Prioridad: {caso.get_prioridad_display()}
Municipio: {caso.municipio}"""
            )
        
        # Mensaje de éxito
        if sla_vencido:
            messages.warning(request, 'Relevamiento iniciado. ADVERTENCIA: SLA vencido - el inicio se registró fuera de término.')
        else:
            messages.success(request, 'Relevamiento iniciado exitosamente. Tarea en proceso.')
        
        # Redirigir al formulario de relevamiento
        return redirect('legajos:nachec_formulario_relevamiento', caso_id=caso.id)
    
    # GET: Mostrar modal de confirmación
    # Validación de acceso en GET también
    if request.user.id != caso.territorial_id:
        messages.error(request, 'Solo el territorial asignado puede iniciar el relevamiento')
        return HttpResponseForbidden('Acceso denegado')
    
    if caso.estado != 'ASIGNADO':
        messages.error(request, 'El caso no está en estado ASIGNADO')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Calcular SLA
    sla_vencido = False
    if caso.sla_relevamiento:
        dias_restantes = (caso.sla_relevamiento - timezone.now().date()).days
        if dias_restantes < 0:
            sla_texto = f"Vencido hace {abs(dias_restantes)} días"
            sla_vencido = True
        elif dias_restantes == 0:
            sla_texto = "Vence hoy"
        else:
            sla_texto = f"Vence en {dias_restantes} días"
    else:
        sla_texto = "No definido"
    
    return render(request, 'legajos/nachec/modal_iniciar_relevamiento.html', {
        'caso': caso,
        'sla_texto': sla_texto,
        'sla_vencido': sla_vencido
    })


@login_required
def finalizar_relevamiento(request, caso_id):
    """EN_RELEVAMIENTO → EVALUADO con validaciones y scoring"""
    from django.utils import timezone
    from django.db import transaction
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from django.contrib.contenttypes.models import ContentType
    from legajos.models import Adjunto
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Validación 1: Estado
    if caso.estado != 'EN_RELEVAMIENTO':
        messages.error(request, 'El caso no está en relevamiento')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 2: Control de acceso
    if request.user.id != caso.territorial_id:
        messages.error(request, 'Solo el territorial asignado puede finalizar el relevamiento')
        return HttpResponseForbidden('Acceso denegado')
    
    # Obtener relevamiento (el último no completado)
    try:
        relevamiento = RelevamientoNachec.objects.filter(caso=caso, completado=False).latest('creado')
    except RelevamientoNachec.DoesNotExist:
        messages.error(request, 'No existe relevamiento activo para este caso')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        # Validaciones para modal
        validaciones = {}
        
        # Completitud del relevamiento
        validaciones['relevamiento_completo'] = relevamiento.is_completo()
        validaciones['faltantes'] = relevamiento.faltantes_por_seccion()
        
        # Evidencias del relevamiento (no del caso)
        content_type = ContentType.objects.get_for_model(RelevamientoNachec)
        adjuntos = Adjunto.objects.filter(content_type=content_type, object_id=relevamiento.id)
        validaciones['cantidad_evidencias'] = adjuntos.count()
        
        # Evidencia obligatoria si hay riesgos críticos
        riesgo_critico = (
            relevamiento.urgencia_alimentaria or 
            relevamiento.hay_violencia or 
            relevamiento.tipo_vivienda in ['PRECARIA', 'CALLE']
        )
        validaciones['riesgo_critico'] = riesgo_critico
        validaciones['evidencia_obligatoria'] = riesgo_critico and adjuntos.count() == 0
        
        # Calcular scoring
        score_total, score_categoria, score_detalle = relevamiento.calcular_scoring()
        
        # SLA
        sla_vencido = False
        if caso.sla_relevamiento:
            dias_restantes = (caso.sla_relevamiento - timezone.now().date()).days
            if dias_restantes < 0:
                sla_texto = f"Vencido hace {abs(dias_restantes)} días"
                sla_vencido = True
            elif dias_restantes == 0:
                sla_texto = "Vence hoy"
            else:
                sla_texto = f"Vence en {dias_restantes} días"
        else:
            sla_texto = "No definido"
        
        puede_finalizar = validaciones['relevamiento_completo'] and not validaciones['evidencia_obligatoria']
        
        return render(request, 'legajos/nachec/modal_finalizar_relevamiento.html', {
            'caso': caso,
            'relevamiento': relevamiento,
            'validaciones': validaciones,
            'adjuntos': adjuntos,
            'score_total': score_total,
            'score_categoria': score_categoria,
            'score_detalle': score_detalle,
            'sla_texto': sla_texto,
            'sla_vencido': sla_vencido,
            'puede_finalizar': puede_finalizar
        })
    
    # POST: Procesar finalización
    if request.method == 'POST':
        # Validación de concurrencia e idempotencia
        caso.refresh_from_db()
        relevamiento.refresh_from_db()
        
        if caso.estado != 'EN_RELEVAMIENTO':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        if relevamiento.completado:
            messages.warning(request, 'Este relevamiento ya fue finalizado')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validación hard: relevamiento completo
        if not relevamiento.is_completo():
            faltantes = relevamiento.faltantes_por_seccion()
            msg_faltantes = []
            for seccion, campos in faltantes.items():
                if campos:
                    msg_faltantes.append(f"{seccion.title()}: {', '.join(campos)}")
            messages.error(request, f'No se puede finalizar. Faltan campos: {" | ".join(msg_faltantes)}')
            return redirect('legajos:nachec_finalizar_relevamiento', caso_id=caso.id)
        
        # Validación hard: evidencia si hay riesgo crítico (del relevamiento)
        content_type = ContentType.objects.get_for_model(RelevamientoNachec)
        adjuntos = Adjunto.objects.filter(content_type=content_type, object_id=relevamiento.id)
        riesgo_critico = (
            relevamiento.urgencia_alimentaria or 
            relevamiento.hay_violencia or 
            relevamiento.tipo_vivienda in ['PRECARIA', 'CALLE']
        )
        
        if riesgo_critico and adjuntos.count() == 0:
            messages.error(request, 'No se puede finalizar: debe adjuntar evidencia por situación de riesgo crítico (urgencia alimentaria, violencia o vivienda precaria/calle)')
            return redirect('legajos:nachec_finalizar_relevamiento', caso_id=caso.id)
        
        # Observaciones de cierre
        observaciones_cierre = request.POST.get('observaciones_cierre', '').strip()
        if len(observaciones_cierre) < 10:
            messages.error(request, 'Las observaciones de cierre deben tener al menos 10 caracteres')
            return redirect('legajos:nachec_finalizar_relevamiento', caso_id=caso.id)
        
        # Transacción atómica
        with transaction.atomic():
            # 1. Calcular y guardar scoring
            score_total, score_categoria, score_detalle = relevamiento.calcular_scoring()
            relevamiento.score_total = score_total
            relevamiento.score_categoria = score_categoria
            relevamiento.score_detalle = score_detalle
            relevamiento.score_version = 'v1'
            relevamiento.completado = True
            relevamiento.fecha_finalizacion = timezone.now()
            relevamiento.observaciones_cierre = observaciones_cierre
            relevamiento.save()
            
            # 2. Cambiar estado del caso
            estado_anterior = caso.estado
            caso.estado = 'EVALUADO'
            caso.fecha_relevamiento = timezone.now().date()
            caso.save()
            
            # 3. Cerrar tarea RELEVAMIENTO (la activa del territorial)
            tarea_relevamiento = TareaNachec.objects.filter(
                caso=caso,
                tipo='RELEVAMIENTO',
                asignado_a=caso.territorial,
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea_relevamiento:
                tarea_relevamiento.estado = 'COMPLETADA'
                tarea_relevamiento.fecha_completada = timezone.now()
                tarea_relevamiento.resultado = f"Relevamiento finalizado. Score: {score_total} ({score_categoria}). Versión: v1"
                tarea_relevamiento.save()
            
            # 4. Crear tarea EVALUACION para coordinador (idempotente)
            tarea_evaluacion_existente = TareaNachec.objects.filter(
                caso=caso,
                tipo='OTRO',
                titulo__icontains='Evaluar caso',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            # SLA evaluación según prioridad
            sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(caso.prioridad, 2)
            sla_evaluacion = timezone.now() + timedelta(days=sla_dias)
            
            if not tarea_evaluacion_existente:
                TareaNachec.objects.create(
                    caso=caso,
                    tipo='OTRO',
                    titulo='Evaluar caso y definir plan de intervención',
                    descripcion=f"""Relevamiento finalizado. Debe evaluar el caso y definir plan de intervención.

Scoring de vulnerabilidad (v1):
- Total: {score_total}/100
- Categoría: {score_categoria}
- Familia: {score_detalle.get('familia', 0)}/15
- Ingresos: {score_detalle.get('ingresos', 0)}/25
- Vivienda: {score_detalle.get('vivienda', 0)}/20
- Salud: {score_detalle.get('salud', 0)}/25
- Riesgos: {score_detalle.get('riesgos', 0)}/15

Observaciones del territorial:
{observaciones_cierre}

Evidencias adjuntas: {adjuntos.count()}
Riesgo crítico: {'Sí' if riesgo_critico else 'No'}""",
                    asignado_a=caso.coordinador or request.user,
                    creado_por=request.user,
                    estado='PENDIENTE',
                    prioridad=caso.prioridad,
                    fecha_vencimiento=sla_evaluacion.date()
                )
            
            # 5. Auditoría enriquecida
            sla_cumplido = caso.sla_relevamiento and timezone.now().date() <= caso.sla_relevamiento
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Relevamiento finalizado por {request.user.get_full_name()}
Score: {score_total}/100 ({score_categoria}) [v1]
Evidencias: {adjuntos.count()}
Riesgo crítico: {'Sí' if riesgo_critico else 'No'}
SLA cumplido: {'Sí' if sla_cumplido else 'No'}
Observaciones: {observaciones_cierre[:100]}..."""
            )
        
        messages.success(request, f'Relevamiento finalizado. Caso pasó a EVALUADO. Score: {score_total} ({score_categoria})')
        return redirect('legajos:programa_detalle', pk=2)


@login_required
def evaluar_caso(request, caso_id):
    """EVALUADO → PLAN_DEFINIDO con evaluación profesional"""
    from django.utils import timezone
    from django.db import transaction
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from .models_nachec import EvaluacionVulnerabilidad
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Validación 1: Estado
    if caso.estado != 'EVALUADO':
        messages.error(request, 'El caso no está en estado EVALUADO')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 2: Control de acceso - solo quien tiene tarea EVALUACION asignada
    tarea_evaluacion = TareaNachec.objects.filter(
        caso=caso,
        tipo='OTRO',
        titulo__icontains='Evaluar caso',
        asignado_a=request.user,
        estado__in=['PENDIENTE', 'EN_PROCESO']
    ).first()
    
    if not tarea_evaluacion:
        messages.error(request, 'No tienes tarea de evaluación asignada para este caso')
        return HttpResponseForbidden('Acceso denegado: sin tarea asignada')
    
    # Obtener relevamiento finalizado
    try:
        relevamiento = RelevamientoNachec.objects.filter(caso=caso, completado=True).latest('fecha_finalizacion')
    except RelevamientoNachec.DoesNotExist:
        messages.error(request, 'No existe relevamiento finalizado para este caso')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        # Datos para el modal
        from django.contrib.contenttypes.models import ContentType
        from legajos.models import Adjunto
        
        content_type = ContentType.objects.get_for_model(RelevamientoNachec)
        adjuntos = Adjunto.objects.filter(content_type=content_type, object_id=relevamiento.id)
        
        return render(request, 'legajos/nachec/modal_evaluar_caso.html', {
            'caso': caso,
            'relevamiento': relevamiento,
            'adjuntos': adjuntos,
            'tarea': tarea_evaluacion
        })
    
    # POST: Procesar acción
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        # Validación de concurrencia
        caso.refresh_from_db()
        if caso.estado != 'EVALUADO':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        if accion == 'confirmar':
            return _confirmar_evaluacion(request, caso, relevamiento, tarea_evaluacion)
        elif accion == 'ampliacion':
            return _solicitar_ampliacion(request, caso, tarea_evaluacion)
        elif accion == 'rechazar':
            return _rechazar_caso(request, caso, tarea_evaluacion)
        else:
            messages.error(request, 'Acción inválida')
            return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)


def _confirmar_evaluacion(request, caso, relevamiento, tarea_evaluacion):
    """Confirmar evaluación y crear plan"""
    from django.utils import timezone
    from django.db import transaction
    from .models_nachec import EvaluacionVulnerabilidad, PlanIntervencionNachec
    
    # Validaciones
    dictamen = request.POST.get('dictamen', '').strip()
    categoria_final = request.POST.get('categoria_final')
    componentes = request.POST.getlist('componentes')
    
    if len(dictamen) < 20:
        messages.error(request, 'El dictamen debe tener al menos 20 caracteres')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    if not categoria_final:
        messages.error(request, 'Debe seleccionar una categoría final')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    if not componentes:
        messages.error(request, 'Debe seleccionar al menos un componente del plan')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    # Override
    override = categoria_final != relevamiento.score_categoria
    justificacion_override = request.POST.get('justificacion_override', '').strip()
    
    if override and len(justificacion_override) < 20:
        messages.error(request, 'Debe justificar el cambio de categoría (min 20 caracteres)')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    # Transacción atómica
    with transaction.atomic():
        # Idempotencia: verificar si ya existe evaluación
        evaluacion_existente = EvaluacionVulnerabilidad.objects.filter(caso=caso).first()
        if evaluacion_existente:
            messages.warning(request, 'Este caso ya fue evaluado')
            return redirect('legajos:programa_detalle', pk=2)
        
        # 1. Crear evaluación
        evaluacion = EvaluacionVulnerabilidad.objects.create(
            caso=caso,
            relevamiento=relevamiento,
            evaluador=request.user,
            score_total=relevamiento.score_total,
            score_version=relevamiento.score_version,
            categoria_sugerida=relevamiento.score_categoria,
            dictamen=dictamen,
            categoria_final=categoria_final,
            override_categoria=override,
            justificacion_override=justificacion_override if override else ''
        )
        
        # 2. Crear plan (desactivar otros planes vigentes)
        PlanIntervencionNachec.objects.filter(caso=caso, vigente=True).update(vigente=False)
        
        plan = PlanIntervencionNachec.objects.create(
            caso=caso,
            referente=request.user,
            objetivo_general=f"Plan de intervención para caso con vulnerabilidad {categoria_final}",
            fecha_inicio=timezone.now().date(),
            horizonte_dias=90,
            incluye_alimentacion='ALIMENTARIA' in componentes,
            incluye_vivienda='VIVIENDA' in componentes,
            incluye_empleo='EMPLEO' in componentes,
            incluye_salud='SALUD' in componentes,
            incluye_educacion='EDUCACION' in componentes,
            incluye_emprendimiento='EMPRENDIMIENTO' in componentes,
            vigente=False,
            observaciones=f"Componentes: {', '.join(componentes)}"
        )
        
        # 3. Cambiar estado del caso y guardar coordinador
        estado_anterior = caso.estado
        caso.estado = 'PLAN_DEFINIDO'
        caso.fecha_evaluacion = timezone.now().date()
        if not caso.coordinador:
            caso.coordinador = request.user
        caso.save()
        
        # 4. Cerrar tarea EVALUACION
        tarea_evaluacion.estado = 'COMPLETADA'
        tarea_evaluacion.fecha_completada = timezone.now()
        tarea_evaluacion.resultado = f"Evaluado. Categoría: {categoria_final}. Plan definido con {len(componentes)} componentes."
        tarea_evaluacion.save()
        
        # 5. Crear tarea ACTIVACION_PLAN (idempotente)
        tarea_activacion_existente = TareaNachec.objects.filter(
            caso=caso,
            tipo='OTRO',
            titulo__icontains='Activar plan',
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).first()
        
        if not tarea_activacion_existente:
            sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(caso.prioridad or 'MEDIA', 2)
            TareaNachec.objects.create(
                caso=caso,
                tipo='OTRO',
                titulo='Activar plan de intervención',
                descripcion=f"""Plan definido. Debe activar y programar prestaciones.

Categoría final: {categoria_final}
Componentes: {', '.join(componentes)}

Dictamen:
{dictamen}

Score: {relevamiento.score_total} ({relevamiento.score_categoria} → {categoria_final})
Override: {'Sí - ' + justificacion_override if override else 'No'}""",
                asignado_a=caso.coordinador or request.user,
                creado_por=request.user,
                estado='PENDIENTE',
                prioridad=caso.prioridad or 'MEDIA',
                fecha_vencimiento=(timezone.now() + timedelta(days=sla_dias)).date()
            )
        
        # 6. Auditoría
        HistorialEstadoCaso.objects.create(
            caso=caso,
            estado_anterior=estado_anterior,
            estado_nuevo=caso.estado,
            usuario=request.user,
            observacion=f"""Evaluación completada por {request.user.get_full_name()}
Categoría: {relevamiento.score_categoria} → {categoria_final}
Override: {'Sí' if override else 'No'}
{'Justificación: ' + justificacion_override if override else ''}
Componentes: {', '.join(componentes)}
Score: {relevamiento.score_total} [v{relevamiento.score_version}]
Dictamen: {dictamen[:100]}..."""
        )
    
    messages.success(request, f'Evaluación completada. Plan definido con categoría {categoria_final}.')
    return redirect('legajos:programa_detalle', pk=2)


def _solicitar_ampliacion(request, caso, tarea_evaluacion):
    """Solicitar ampliación de relevamiento"""
    from django.utils import timezone
    from django.db import transaction
    
    motivo = request.POST.get('motivo_ampliacion')
    detalle = request.POST.get('detalle_ampliacion', '').strip()
    plazo_horas = int(request.POST.get('plazo_ampliacion', 48))
    
    if len(detalle) < 20:
        messages.error(request, 'El detalle de ampliación debe tener al menos 20 caracteres')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    with transaction.atomic():
        # 1. Volver caso a EN_RELEVAMIENTO
        estado_anterior = caso.estado
        caso.estado = 'EN_RELEVAMIENTO'
        caso.save()
        
        # 2. Crear/reabrir tarea RELEVAMIENTO
        fecha_limite = timezone.now() + timedelta(hours=plazo_horas)
        TareaNachec.objects.create(
            caso=caso,
            tipo='AMPLIACION',
            titulo='Ampliación de relevamiento solicitada',
            descripcion=f"""Ampliación solicitada por evaluador.

Motivo: {motivo}
Detalle: {detalle}
Plazo: {plazo_horas}h

Debe completar información faltante y volver a finalizar relevamiento.""",
            asignado_a=caso.territorial,
            creado_por=request.user,
            estado='PENDIENTE',
            prioridad=caso.prioridad,
            fecha_vencimiento=fecha_limite.date()
        )
        
        # 3. Tarea EVALUACION queda EN_PROCESO
        tarea_evaluacion.estado = 'EN_PROCESO'
        tarea_evaluacion.resultado = f"Ampliación solicitada: {motivo}"
        tarea_evaluacion.save()
        
        # 4. Auditoría
        HistorialEstadoCaso.objects.create(
            caso=caso,
            estado_anterior=estado_anterior,
            estado_nuevo=caso.estado,
            usuario=request.user,
            observacion=f"""Ampliación solicitada por {request.user.get_full_name()}
Motivo: {motivo}
Plazo: {plazo_horas}h
Detalle: {detalle}"""
        )
    
    messages.warning(request, f'Ampliación solicitada. Caso vuelve a EN_RELEVAMIENTO con plazo de {plazo_horas}h.')
    return redirect('legajos:programa_detalle', pk=2)


def _rechazar_caso(request, caso, tarea_evaluacion):
    """Rechazar caso"""
    from django.utils import timezone
    from django.db import transaction
    
    motivo = request.POST.get('motivo_rechazo')
    observaciones = request.POST.get('observaciones_rechazo', '').strip()
    
    if len(observaciones) < 20:
        messages.error(request, 'Las observaciones de rechazo deben tener al menos 20 caracteres')
        return redirect('legajos:nachec_evaluar_caso', caso_id=caso.id)
    
    with transaction.atomic():
        # 1. Cambiar estado
        estado_anterior = caso.estado
        caso.estado = 'RECHAZADO'
        caso.motivo_rechazo = f"{motivo}: {observaciones}"
        caso.fecha_cierre = timezone.now().date()
        caso.save()
        
        # 2. Cerrar tarea EVALUACION
        tarea_evaluacion.estado = 'COMPLETADA'
        tarea_evaluacion.fecha_completada = timezone.now()
        tarea_evaluacion.resultado = f"Caso rechazado: {motivo}"
        tarea_evaluacion.save()
        
        # 3. Cancelar tareas abiertas del caso
        TareaNachec.objects.filter(
            caso=caso,
            estado__in=['PENDIENTE', 'EN_PROCESO']
        ).exclude(id=tarea_evaluacion.id).update(
            estado='CANCELADA',
            resultado=f"Cancelada por rechazo del caso: {motivo}"
        )
        
        # 4. Auditoría
        HistorialEstadoCaso.objects.create(
            caso=caso,
            estado_anterior=estado_anterior,
            estado_nuevo=caso.estado,
            usuario=request.user,
            observacion=f"""Caso rechazado por {request.user.get_full_name()}
Motivo: {motivo}
Observaciones: {observaciones}"""
        )
    
    messages.info(request, f'Caso rechazado: {motivo}')
    return redirect('legajos:programa_detalle', pk=2)


@login_required
def activar_plan(request, caso_id):
    """PLAN_DEFINIDO → EN_EJECUCION con programación de prestaciones"""
    from django.utils import timezone
    from django.db import transaction
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from django.contrib.auth.models import User
    from .models_nachec import PlanIntervencionNachec, PrestacionNachec
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Validación 1: Estado
    if caso.estado != 'PLAN_DEFINIDO':
        messages.error(request, 'El caso no tiene plan definido')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 2: Control de acceso - solo quien tiene tarea ACTIVACION_PLAN
    tarea_activacion = TareaNachec.objects.filter(
        caso=caso,
        tipo='OTRO',
        titulo__icontains='Activar plan',
        asignado_a=request.user,
        estado__in=['PENDIENTE', 'EN_PROCESO']
    ).first()
    
    if not tarea_activacion:
        messages.error(request, 'No tienes tarea de activación asignada para este caso')
        return HttpResponseForbidden('Acceso denegado: sin tarea asignada')
    
    # Obtener plan
    plan = PlanIntervencionNachec.objects.filter(caso=caso).order_by('-creado').first()
    if not plan:
        messages.error(request, 'No existe plan para este caso')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 3: Idempotencia - plan ya activado
    if plan.vigente or plan.fecha_activacion:
        messages.warning(request, 'El plan ya fue activado')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        # Obtener evaluación
        evaluacion = caso.evaluacion if hasattr(caso, 'evaluacion') else None
        
        # Componentes activos
        componentes = []
        if plan.incluye_alimentacion:
            componentes.append({'codigo': 'ALIMENTARIA', 'nombre': 'Alimentación', 'icono': 'utensils', 'color': 'orange'})
        if plan.incluye_vivienda:
            componentes.append({'codigo': 'VIVIENDA', 'nombre': 'Vivienda', 'icono': 'home', 'color': 'blue'})
        if plan.incluye_salud:
            componentes.append({'codigo': 'SALUD', 'nombre': 'Salud', 'icono': 'heartbeat', 'color': 'red'})
        if plan.incluye_educacion:
            componentes.append({'codigo': 'EDUCACION', 'nombre': 'Educación', 'icono': 'graduation-cap', 'color': 'purple'})
        if plan.incluye_empleo:
            componentes.append({'codigo': 'EMPLEO', 'nombre': 'Empleo/Capacitación', 'icono': 'briefcase', 'color': 'green'})
        if plan.incluye_emprendimiento:
            componentes.append({'codigo': 'EMPRENDIMIENTO', 'nombre': 'Emprendimiento', 'icono': 'lightbulb', 'color': 'yellow'})
        
        # Usuarios disponibles como responsables
        usuarios = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        return render(request, 'legajos/nachec/modal_activar_plan.html', {
            'caso': caso,
            'plan': plan,
            'evaluacion': evaluacion,
            'componentes': componentes,
            'usuarios': usuarios,
            'tarea': tarea_activacion
        })
    
    # POST: Procesar activación
    if request.method == 'POST':
        # Validación de concurrencia
        caso.refresh_from_db()
        plan.refresh_from_db()
        
        if caso.estado != 'PLAN_DEFINIDO':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        if plan.vigente or plan.fecha_activacion:
            messages.warning(request, 'El plan ya fue activado')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validar confirmación
        confirmacion = request.POST.get('confirmacion')
        if not confirmacion:
            messages.error(request, 'Debe confirmar la activación del plan')
            return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
        
        # Obtener datos por componente
        componentes_data = []
        componentes_activos = []
        
        if plan.incluye_alimentacion:
            componentes_activos.append('ALIMENTARIA')
        if plan.incluye_vivienda:
            componentes_activos.append('VIVIENDA')
        if plan.incluye_salud:
            componentes_activos.append('SALUD')
        if plan.incluye_educacion:
            componentes_activos.append('EDUCACION')
        if plan.incluye_empleo:
            componentes_activos.append('EMPLEO')
        if plan.incluye_emprendimiento:
            componentes_activos.append('EMPRENDIMIENTO')
        
        # Validar datos por componente
        for comp in componentes_activos:
            responsable_id = request.POST.get(f'responsable_{comp}')
            fecha_inicio = request.POST.get(f'fecha_inicio_{comp}')
            frecuencia = request.POST.get(f'frecuencia_{comp}', 'UNICA')
            observaciones = request.POST.get(f'observaciones_{comp}', '')
            
            if not responsable_id:
                messages.error(request, f'Debe asignar responsable para {comp}')
                return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            
            if not fecha_inicio:
                messages.error(request, f'Debe especificar fecha de inicio para {comp}')
                return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            
            # Validar fecha
            from datetime import datetime
            try:
                fecha_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                if fecha_obj < timezone.now().date():
                    messages.error(request, f'La fecha de inicio para {comp} no puede ser anterior a hoy')
                    return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            except ValueError:
                messages.error(request, f'Formato de fecha inválido para {comp}')
                return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            
            try:
                responsable = User.objects.get(id=responsable_id, is_active=True)
            except User.DoesNotExist:
                messages.error(request, f'Responsable inválido para {comp}')
                return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            
            componentes_data.append({
                'tipo': comp,
                'responsable': responsable,
                'fecha_inicio': fecha_obj,
                'frecuencia': frecuencia,
                'observaciones': observaciones
            })
        
        # Transacción atómica
        with transaction.atomic():
            # 1. Activar plan y desactivar otros (plan vigente único)
            PlanIntervencionNachec.objects.filter(
                caso=caso,
                vigente=True
            ).exclude(id=plan.id).update(vigente=False)
            
            plan.vigente = True
            plan.fecha_activacion = timezone.now()
            plan.save()
            
            # 2. Crear prestaciones (idempotente)
            prestaciones_creadas = 0
            tareas_creadas = 0
            
            # SLA por componente y prioridad (días)
            sla_config = {
                'ALIMENTARIA': {'URGENTE': 1, 'ALTA': 3, 'MEDIA': 7, 'BAJA': 7},
                'VIVIENDA': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'SALUD': {'URGENTE': 3, 'ALTA': 7, 'MEDIA': 15, 'BAJA': 15},
                'EDUCACION': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'EMPLEO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'EMPRENDIMIENTO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30}
            }
            
            for comp_data in componentes_data:
                # Calcular SLA
                sla_dias = sla_config.get(comp_data['tipo'], {}).get(caso.prioridad or 'MEDIA', 15)
                sla_hasta = timezone.now() + timedelta(days=sla_dias)
                
                # Verificar si ya existe prestación activa
                prestacion_existente = PrestacionNachec.objects.filter(
                    plan=plan,
                    caso=caso,
                    tipo=comp_data['tipo'],
                    estado__in=['CREADA', 'PROGRAMADA', 'EN_PROCESO', 'EN_CURSO']
                ).first()
                
                if prestacion_existente:
                    # Actualizar
                    prestacion_existente.responsable = comp_data['responsable']
                    prestacion_existente.fecha_programada = comp_data['fecha_inicio']
                    prestacion_existente.frecuencia = comp_data['frecuencia']
                    prestacion_existente.sla_hasta = sla_hasta
                    prestacion_existente.observaciones = comp_data['observaciones']
                    prestacion_existente.save()
                    prestacion = prestacion_existente
                else:
                    # Crear nueva
                    prestacion = PrestacionNachec.objects.create(
                        plan=plan,
                        caso=caso,
                        tipo=comp_data['tipo'],
                        descripcion=f"Prestación de {comp_data['tipo'].lower()} - {caso.ciudadano_titular.nombre_completo}",
                        estado='PROGRAMADA',
                        frecuencia=comp_data['frecuencia'],
                        fecha_programada=comp_data['fecha_inicio'],
                        sla_hasta=sla_hasta,
                        responsable=comp_data['responsable'],
                        observaciones=comp_data['observaciones']
                    )
                    prestaciones_creadas += 1
                
                # Crear tarea de entrega (idempotente)
                tarea_existente = TareaNachec.objects.filter(
                    caso=caso,
                    prestacion=prestacion,
                    tipo='ENTREGA',
                    estado__in=['PENDIENTE', 'EN_PROCESO']
                ).first()
                
                if not tarea_existente:
                    TareaNachec.objects.create(
                        caso=caso,
                        prestacion=prestacion,
                        tipo='ENTREGA',
                        titulo=f"Ejecutar prestación: {comp_data['tipo']}",
                        descripcion=f"""Prestación programada para {caso.ciudadano_titular.nombre_completo}

Tipo: {comp_data['tipo']}
Frecuencia: {comp_data['frecuencia']}
Fecha programada: {comp_data['fecha_inicio'].strftime('%d/%m/%Y')}

Observaciones:
{comp_data['observaciones']}""",
                        asignado_a=comp_data['responsable'],
                        creado_por=request.user,
                        estado='PENDIENTE',
                        prioridad=caso.prioridad or 'MEDIA',
                        fecha_vencimiento=sla_hasta.date()
                    )
                    tareas_creadas += 1
            
            # 3. Cambiar estado del caso (solo si hay prestaciones)
            if prestaciones_creadas > 0 or PrestacionNachec.objects.filter(plan=plan).exists():
                estado_anterior = caso.estado
                caso.estado = 'EN_EJECUCION'
                caso.save()
            else:
                messages.error(request, 'No se pudieron crear prestaciones. Plan no activado.')
                return redirect('legajos:nachec_activar_plan', caso_id=caso.id)
            
            # 4. Cerrar tarea ACTIVACION_PLAN
            tarea_activacion.estado = 'COMPLETADA'
            tarea_activacion.fecha_completada = timezone.now()
            tarea_activacion.resultado = f"Plan activado. {prestaciones_creadas} prestaciones creadas, {tareas_creadas} tareas generadas."
            tarea_activacion.save()
            
            # 5. Auditoría
            componentes_str = ', '.join([c['tipo'] for c in componentes_data])
            responsables_str = ', '.join([f"{c['tipo']}: {c['responsable'].get_full_name()}" for c in componentes_data])
            
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Plan activado por {request.user.get_full_name()}
Componentes: {componentes_str}
Responsables: {responsables_str}
Prestaciones: {prestaciones_creadas} creadas
Tareas: {tareas_creadas} generadas"""
            )
        
        messages.success(request, f'Plan activado exitosamente. Se crearon {prestaciones_creadas} prestaciones y {tareas_creadas} tareas de ejecución.')
        return redirect('legajos:programa_detalle', pk=2)


@login_required
def pasar_a_seguimiento(request, caso_id):
    """EN_EJECUCION → EN_SEGUIMIENTO"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if caso.estado != 'EN_EJECUCION':
        messages.error(request, 'El caso no está en ejecución')
        return redirect('legajos:programa_detalle', pk=2)
    
    estado_anterior = caso.estado
    caso.estado = 'EN_SEGUIMIENTO'
    caso.save()
    
    HistorialEstadoCaso.objects.create(
        caso=caso,
        estado_anterior=estado_anterior,
        estado_nuevo=caso.estado,
        usuario=request.user
    )
    
    messages.success(request, 'Caso en seguimiento')
    return redirect('legajos:programa_detalle', pk=2)


@login_required
def cerrar_caso(request, caso_id):
    """EN_SEGUIMIENTO → CERRADO"""
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if caso.estado != 'EN_SEGUIMIENTO':
        messages.error(request, 'El caso no está en seguimiento')
        return redirect('legajos:programa_detalle', pk=2)
    
    estado_anterior = caso.estado
    caso.estado = 'CERRADO'
    caso.save()
    
    HistorialEstadoCaso.objects.create(
        caso=caso,
        estado_anterior=estado_anterior,
        estado_nuevo=caso.estado,
        usuario=request.user
    )
    
    messages.success(request, 'Caso cerrado')
    return redirect('legajos:programa_detalle', pk=2)


@login_required
def formulario_relevamiento(request, caso_id):
    """Formulario de relevamiento sociofamiliar"""
    from .models_nachec import RelevamientoNachec
    from django.shortcuts import render
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    if request.method == 'POST':
        # Crear o actualizar relevamiento
        relevamiento, created = RelevamientoNachec.objects.get_or_create(
            caso=caso,
            defaults={
                'territorial': request.user,
                'cantidad_convivientes': int(request.POST.get('cantidad_convivientes', 0) or 0),
                'frecuencia_comidas': int(request.POST.get('frecuencia_comidas', 0) or 0)
            }
        )
        
        # Guardar datos del formulario
        relevamiento.cantidad_convivientes = int(request.POST.get('cantidad_convivientes', 0) or 0)
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
        relevamiento.frecuencia_comidas = int(request.POST.get('frecuencia_comidas', 0) or 0)
        relevamiento.hay_violencia = request.POST.get('hay_violencia') == 'on'
        relevamiento.urgencia_alimentaria = request.POST.get('urgencia_alimentaria') == 'on'
        relevamiento.observaciones = request.POST.get('observaciones', '')
        relevamiento.completado = True
        
        from django.utils import timezone
        relevamiento.fecha_finalizacion = timezone.now()
        relevamiento.save()
        
        messages.success(request, 'Relevamiento guardado exitosamente')
        return redirect('legajos:programa_detalle', pk=2)
    
    # GET: Mostrar formulario
    try:
        relevamiento = RelevamientoNachec.objects.get(caso=caso)
    except RelevamientoNachec.DoesNotExist:
        relevamiento = None
    
    return render(request, 'legajos/nachec/formulario_relevamiento.html', {
        'caso': caso,
        'relevamiento': relevamiento
    })


# ============================================================================
# PASO 8 - Gestión de Prestaciones
# ============================================================================

@login_required
def iniciar_prestacion(request, prestacion_id):
    """PROGRAMADA → EN_PROCESO"""
    from django.http import HttpResponseForbidden
    from .models_nachec import PrestacionNachec
    
    prestacion = get_object_or_404(PrestacionNachec, id=prestacion_id)
    
    # Validación 1: Solo responsable
    if request.user.id != prestacion.responsable_id:
        messages.error(request, 'Solo el responsable puede iniciar esta prestación')
        return HttpResponseForbidden('Acceso denegado')
    
    # Validación 2: Estado PROGRAMADA
    if prestacion.estado != 'PROGRAMADA':
        messages.error(request, 'La prestación no está en estado PROGRAMADA')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        
        with transaction.atomic():
            # 1. Cambiar estado prestación
            prestacion.estado = 'EN_PROCESO'
            prestacion.save()
            
            # 2. Actualizar tarea ENTREGA asociada
            tarea = TareaNachec.objects.filter(
                prestacion=prestacion,
                tipo='ENTREGA',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea and tarea.estado == 'PENDIENTE':
                tarea.estado = 'EN_PROCESO'
                tarea.save()
            
            # 3. Auditoría
            HistorialEstadoCaso.objects.create(
                caso=prestacion.caso,
                estado_anterior=prestacion.caso.estado,
                estado_nuevo=prestacion.caso.estado,
                usuario=request.user,
                observacion=f"""Prestación iniciada: {prestacion.get_tipo_display()}
Responsable: {request.user.get_full_name()}
SLA: {prestacion.sla_hasta.strftime('%d/%m/%Y %H:%M') if prestacion.sla_hasta else 'No definido'}
Fecha programada: {prestacion.fecha_programada.strftime('%d/%m/%Y') if prestacion.fecha_programada else 'No definida'}"""
            )
        
        messages.success(request, f'Prestación {prestacion.get_tipo_display()} iniciada')
        return redirect('legajos:programa_detalle', pk=2)
    
    return redirect('legajos:programa_detalle', pk=2)


@login_required
def confirmar_entrega_prestacion(request, prestacion_id):
    """EN_PROCESO → ENTREGADA con generación de próxima si frecuencia != UNICA"""
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from django.contrib.contenttypes.models import ContentType
    from legajos.models import Adjunto
    from .models_nachec import PrestacionNachec
    
    prestacion = get_object_or_404(PrestacionNachec, id=prestacion_id)
    
    # Validación 1: Solo responsable
    if request.user.id != prestacion.responsable_id:
        messages.error(request, 'Solo el responsable puede confirmar esta prestación')
        return HttpResponseForbidden('Acceso denegado')
    
    # Validación 2: Estado EN_PROCESO o EN_CURSO (compat)
    if prestacion.estado not in ['EN_PROCESO', 'EN_CURSO']:
        messages.error(request, 'La prestación no está en proceso')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        # Contar evidencias
        content_type = ContentType.objects.get_for_model(PrestacionNachec)
        adjuntos = Adjunto.objects.filter(content_type=content_type, object_id=prestacion.id)
        
        # Validar evidencia obligatoria para ALIMENTARIA
        evidencia_obligatoria = prestacion.tipo == 'ALIMENTARIA' and adjuntos.count() == 0
        
        return render(request, 'legajos/nachec/modal_confirmar_entrega.html', {
            'prestacion': prestacion,
            'adjuntos': adjuntos,
            'evidencia_obligatoria': evidencia_obligatoria
        })
    
    # POST: Procesar confirmación
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta
        
        # Validaciones
        observaciones_entrega = request.POST.get('observaciones_entrega', '').strip()
        confirmacion = request.POST.get('confirmacion')
        
        if not confirmacion:
            messages.error(request, 'Debe confirmar la entrega')
            return redirect('legajos:nachec_confirmar_entrega', prestacion_id=prestacion.id)
        
        if len(observaciones_entrega) < 10:
            messages.error(request, 'Las observaciones deben tener al menos 10 caracteres')
            return redirect('legajos:nachec_confirmar_entrega', prestacion_id=prestacion.id)
        
        # Validar evidencia para ALIMENTARIA
        content_type = ContentType.objects.get_for_model(PrestacionNachec)
        adjuntos = Adjunto.objects.filter(content_type=content_type, object_id=prestacion.id)
        
        if prestacion.tipo == 'ALIMENTARIA' and adjuntos.count() == 0:
            messages.error(request, 'Debe adjuntar evidencia para prestaciones de tipo ALIMENTARIA')
            return redirect('legajos:nachec_confirmar_entrega', prestacion_id=prestacion.id)
        
        with transaction.atomic():
            # 1. Marcar prestación como entregada
            prestacion.estado = 'ENTREGADA'
            prestacion.fecha_entregada = timezone.now().date()
            prestacion.observaciones = f"{prestacion.observaciones}\n\n[ENTREGA] {observaciones_entrega}"
            prestacion.save()
            
            # 2. Completar tarea ENTREGA
            tarea = TareaNachec.objects.filter(
                prestacion=prestacion,
                tipo='ENTREGA',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            cumplio_sla = False
            if tarea:
                if prestacion.sla_hasta:
                    cumplio_sla = timezone.now() <= prestacion.sla_hasta
                
                tarea.estado = 'COMPLETADA'
                tarea.fecha_completada = timezone.now()
                tarea.resultado = f"""Entrega confirmada.
SLA cumplido: {'Sí' if cumplio_sla else 'No'}
Evidencias: {adjuntos.count()}
Observaciones: {observaciones_entrega}"""
                tarea.save()
            
            # 3. Generar próxima prestación si frecuencia != UNICA
            proxima_creada = False
            if prestacion.frecuencia != 'UNICA':
                # Calcular fecha próxima
                if prestacion.frecuencia == 'SEMANAL':
                    fecha_proxima = prestacion.fecha_entregada + timedelta(days=7)
                elif prestacion.frecuencia == 'QUINCENAL':
                    fecha_proxima = prestacion.fecha_entregada + timedelta(days=14)
                elif prestacion.frecuencia == 'MENSUAL':
                    try:
                        fecha_proxima = prestacion.fecha_entregada + relativedelta(months=1)
                    except:
                        fecha_proxima = prestacion.fecha_entregada + timedelta(days=30)
                else:
                    fecha_proxima = None
                
                if fecha_proxima:
                    # Calcular SLA (reutilizar config de PASO 7)
                    sla_config = {
                        'ALIMENTARIA': {'URGENTE': 1, 'ALTA': 3, 'MEDIA': 7, 'BAJA': 7},
                        'VIVIENDA': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                        'SALUD': {'URGENTE': 3, 'ALTA': 7, 'MEDIA': 15, 'BAJA': 15},
                        'EDUCACION': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                        'EMPLEO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                        'EMPRENDIMIENTO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30}
                    }
                    
                    sla_dias = sla_config.get(prestacion.tipo, {}).get(prestacion.caso.prioridad or 'MEDIA', 15)
                    sla_hasta_proxima = timezone.make_aware(
                        timezone.datetime.combine(fecha_proxima, timezone.datetime.min.time())
                    ) + timedelta(days=sla_dias)
                    
                    # Crear próxima prestación
                    proxima_prestacion = PrestacionNachec.objects.create(
                        plan=prestacion.plan,
                        caso=prestacion.caso,
                        tipo=prestacion.tipo,
                        descripcion=prestacion.descripcion,
                        estado='PROGRAMADA',
                        frecuencia=prestacion.frecuencia,
                        fecha_programada=fecha_proxima,
                        sla_hasta=sla_hasta_proxima,
                        responsable=prestacion.responsable,
                        observaciones=f"Generada automáticamente por frecuencia {prestacion.frecuencia}"
                    )
                    
                    # Crear tarea ENTREGA para próxima prestación
                    TareaNachec.objects.create(
                        caso=prestacion.caso,
                        prestacion=proxima_prestacion,
                        tipo='ENTREGA',
                        titulo=f"Ejecutar prestación: {prestacion.tipo}",
                        descripcion=f"""Prestación programada para {prestacion.caso.ciudadano_titular.nombre_completo}

Tipo: {prestacion.tipo}
Frecuencia: {prestacion.frecuencia}
Fecha programada: {fecha_proxima.strftime('%d/%m/%Y')}

Generada automáticamente por frecuencia.""",
                        asignado_a=prestacion.responsable,
                        creado_por=request.user,
                        estado='PENDIENTE',
                        prioridad=prestacion.caso.prioridad or 'MEDIA',
                        fecha_vencimiento=sla_hasta_proxima.date()
                    )
                    
                    proxima_creada = True
                    
                    # Auditoría regeneración
                    HistorialEstadoCaso.objects.create(
                        caso=prestacion.caso,
                        estado_anterior=prestacion.caso.estado,
                        estado_nuevo=prestacion.caso.estado,
                        usuario=request.user,
                        observacion=f"""Prestación regenerada: {prestacion.get_tipo_display()}
Frecuencia: {prestacion.frecuencia}
Próxima fecha: {fecha_proxima.strftime('%d/%m/%Y')}
SLA próxima: {sla_hasta_proxima.strftime('%d/%m/%Y')}"""
                    )
            
            # 4. Auditoría entrega
            HistorialEstadoCaso.objects.create(
                caso=prestacion.caso,
                estado_anterior=prestacion.caso.estado,
                estado_nuevo=prestacion.caso.estado,
                usuario=request.user,
                observacion=f"""Prestación entregada: {prestacion.get_tipo_display()}
SLA cumplido: {'Sí' if cumplio_sla else 'No'}
Fecha entrega: {prestacion.fecha_entregada.strftime('%d/%m/%Y')}
Evidencias: {adjuntos.count()}
Próxima generada: {'Sí' if proxima_creada else 'No'}
Observaciones: {observaciones_entrega[:100]}..."""
            )
            
            # 5. Recalcular estado del caso (CA6)
            resultado = prestacion.caso.recalcular_estado_por_prestaciones()
            if resultado.get('cambio'):
                motivo = 'sin_prestaciones_activas' if resultado['estado_nuevo'] == 'EN_SEGUIMIENTO' else 'prestacion_activa_detectada'
                HistorialEstadoCaso.objects.create(
                    caso=prestacion.caso,
                    estado_anterior=resultado['estado_anterior'],
                    estado_nuevo=resultado['estado_nuevo'],
                    usuario=request.user,
                    observacion=f"""Transición automática por prestaciones
Motivo: {motivo}
Prestaciones activas: {resultado['prestaciones_activas']}"""
                )
                
                # Crear tarea CIERRE_CASO si pasa a EN_SEGUIMIENTO
                if resultado['estado_nuevo'] == 'EN_SEGUIMIENTO':
                    tarea_cierre_existente = TareaNachec.objects.filter(
                        caso=prestacion.caso,
                        tipo='OTRO',
                        titulo__icontains='Cerrar caso',
                        estado__in=['PENDIENTE', 'EN_PROCESO']
                    ).first()
                    
                    if not tarea_cierre_existente:
                        sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(prestacion.caso.prioridad or 'MEDIA', 2)
                        TareaNachec.objects.create(
                            caso=prestacion.caso,
                            tipo='OTRO',
                            titulo='Cerrar caso - Sin prestaciones activas',
                            descripcion=f"""El caso pasó a EN_SEGUIMIENTO porque no quedan prestaciones activas.

Debe evaluar cierre del caso.

Plan vigente: {prestacion.plan.id}
Última prestación entregada: {prestacion.get_tipo_display()} - {prestacion.fecha_entregada.strftime('%d/%m/%Y')}""",
                            asignado_a=prestacion.caso.coordinador or request.user,
                            creado_por=request.user,
                            estado='PENDIENTE',
                            prioridad=prestacion.caso.prioridad or 'MEDIA',
                            fecha_vencimiento=(timezone.now() + timedelta(days=sla_dias)).date()
                        )
        
        msg = f'Prestación {prestacion.get_tipo_display()} confirmada como entregada'
        if proxima_creada:
            msg += f'. Próxima prestación programada para {fecha_proxima.strftime("%d/%m/%Y")}'
        messages.success(request, msg)
        return redirect('legajos:programa_detalle', pk=2)


@login_required
def reprogramar_prestacion(request, prestacion_id):
    """Reprogramar fecha y recalcular SLA"""
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from .models_nachec import PrestacionNachec
    
    prestacion = get_object_or_404(PrestacionNachec, id=prestacion_id)
    
    # Validación 1: Solo responsable
    if request.user.id != prestacion.responsable_id:
        messages.error(request, 'Solo el responsable puede reprogramar esta prestación')
        return HttpResponseForbidden('Acceso denegado')
    
    # Validación 2: Estado PROGRAMADA o EN_PROCESO/EN_CURSO
    if prestacion.estado not in ['PROGRAMADA', 'EN_PROCESO', 'EN_CURSO']:
        messages.error(request, 'La prestación no puede ser reprogramada en su estado actual')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        from django.utils import timezone
        return render(request, 'legajos/nachec/modal_reprogramar_prestacion.html', {
            'prestacion': prestacion,
            'fecha_minima': timezone.now().date().strftime('%Y-%m-%d')
        })
    
    # POST: Procesar reprogramación
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        from datetime import datetime, timedelta
        
        # Validaciones
        nueva_fecha = request.POST.get('nueva_fecha')
        motivo = request.POST.get('motivo')
        detalle = request.POST.get('detalle', '').strip()
        
        if not nueva_fecha:
            messages.error(request, 'Debe especificar nueva fecha')
            return redirect('legajos:nachec_reprogramar_prestacion', prestacion_id=prestacion.id)
        
        if len(detalle) < 10:
            messages.error(request, 'El detalle debe tener al menos 10 caracteres')
            return redirect('legajos:nachec_reprogramar_prestacion', prestacion_id=prestacion.id)
        
        # Validar fecha
        try:
            fecha_obj = datetime.strptime(nueva_fecha, '%Y-%m-%d').date()
            if fecha_obj < timezone.now().date():
                messages.error(request, 'La fecha no puede ser anterior a hoy')
                return redirect('legajos:nachec_reprogramar_prestacion', prestacion_id=prestacion.id)
        except ValueError:
            messages.error(request, 'Formato de fecha inválido')
            return redirect('legajos:nachec_reprogramar_prestacion', prestacion_id=prestacion.id)
        
        with transaction.atomic():
            # 1. Actualizar prestación
            fecha_anterior = prestacion.fecha_programada
            prestacion.fecha_programada = fecha_obj
            
            # Recalcular SLA (reutilizar config de PASO 7)
            sla_config = {
                'ALIMENTARIA': {'URGENTE': 1, 'ALTA': 3, 'MEDIA': 7, 'BAJA': 7},
                'VIVIENDA': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'SALUD': {'URGENTE': 3, 'ALTA': 7, 'MEDIA': 15, 'BAJA': 15},
                'EDUCACION': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'EMPLEO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30},
                'EMPRENDIMIENTO': {'URGENTE': 7, 'ALTA': 15, 'MEDIA': 30, 'BAJA': 30}
            }
            
            sla_dias = sla_config.get(prestacion.tipo, {}).get(prestacion.caso.prioridad or 'MEDIA', 15)
            prestacion.sla_hasta = timezone.make_aware(
                timezone.datetime.combine(fecha_obj, timezone.datetime.min.time())
            ) + timedelta(days=sla_dias)
            
            prestacion.observaciones = f"{prestacion.observaciones}\n\n[REPROGRAMACIÓN] {motivo}: {detalle}"
            prestacion.save()
            
            # 2. Actualizar tarea ENTREGA asociada
            tarea = TareaNachec.objects.filter(
                prestacion=prestacion,
                tipo='ENTREGA',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea:
                tarea.fecha_vencimiento = prestacion.sla_hasta.date()
                tarea.save()
            
            # 3. Auditoría
            HistorialEstadoCaso.objects.create(
                caso=prestacion.caso,
                estado_anterior=prestacion.caso.estado,
                estado_nuevo=prestacion.caso.estado,
                usuario=request.user,
                observacion=f"""Prestación reprogramada: {prestacion.get_tipo_display()}
Fecha anterior: {fecha_anterior.strftime('%d/%m/%Y') if fecha_anterior else 'No definida'}
Nueva fecha: {fecha_obj.strftime('%d/%m/%Y')}
Nuevo SLA: {prestacion.sla_hasta.strftime('%d/%m/%Y %H:%M')}
Motivo: {motivo}
Detalle: {detalle}"""
            )
        
        messages.success(request, f'Prestación reprogramada para {fecha_obj.strftime("%d/%m/%Y")}')
        return redirect('legajos:programa_detalle', pk=2)


@login_required
def cancelar_prestacion(request, prestacion_id):
    """Cancelar prestación y tarea asociada"""
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from .models_nachec import PrestacionNachec
    
    prestacion = get_object_or_404(PrestacionNachec, id=prestacion_id)
    
    # Validación 1: Solo responsable
    if request.user.id != prestacion.responsable_id:
        messages.error(request, 'Solo el responsable puede cancelar esta prestación')
        return HttpResponseForbidden('Acceso denegado')
    
    # Validación 2: No cancelar si ya entregada/completada
    if prestacion.estado in ['ENTREGADA', 'COMPLETADA']:
        messages.error(request, 'No se puede cancelar una prestación ya entregada')
        return redirect('legajos:programa_detalle', pk=2)
    
    if request.method == 'GET':
        return render(request, 'legajos/nachec/modal_cancelar_prestacion.html', {
            'prestacion': prestacion
        })
    
    # POST: Procesar cancelación
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        
        # Validaciones
        motivo = request.POST.get('motivo')
        detalle = request.POST.get('detalle', '').strip()
        
        if len(detalle) < 10:
            messages.error(request, 'El detalle debe tener al menos 10 caracteres')
            return redirect('legajos:nachec_cancelar_prestacion', prestacion_id=prestacion.id)
        
        with transaction.atomic():
            # 1. Cancelar prestación
            prestacion.estado = 'CANCELADA'
            prestacion.observaciones = f"{prestacion.observaciones}\n\n[CANCELACIÓN] {motivo}: {detalle}"
            prestacion.save()
            
            # 2. Cancelar tarea ENTREGA asociada
            tarea = TareaNachec.objects.filter(
                prestacion=prestacion,
                tipo='ENTREGA',
                estado__in=['PENDIENTE', 'EN_PROCESO']
            ).first()
            
            if tarea:
                tarea.estado = 'CANCELADA'
                tarea.resultado = f"Cancelada: {motivo} - {detalle}"
                tarea.save()
            
            # 3. Auditoría
            HistorialEstadoCaso.objects.create(
                caso=prestacion.caso,
                estado_anterior=prestacion.caso.estado,
                estado_nuevo=prestacion.caso.estado,
                usuario=request.user,
                observacion=f"""Prestación cancelada: {prestacion.get_tipo_display()}
Motivo: {motivo}
Detalle: {detalle}"""
            )
            
            # 4. Recalcular estado del caso (CA6)
            resultado = prestacion.caso.recalcular_estado_por_prestaciones()
            if resultado.get('cambio'):
                motivo_cambio = 'sin_prestaciones_activas' if resultado['estado_nuevo'] == 'EN_SEGUIMIENTO' else 'prestacion_activa_detectada'
                HistorialEstadoCaso.objects.create(
                    caso=prestacion.caso,
                    estado_anterior=resultado['estado_anterior'],
                    estado_nuevo=resultado['estado_nuevo'],
                    usuario=request.user,
                    observacion=f"""Transición automática por prestaciones
Motivo: {motivo_cambio}
Prestaciones activas: {resultado['prestaciones_activas']}"""
                )
                
                # Crear tarea CIERRE_CASO si pasa a EN_SEGUIMIENTO
                if resultado['estado_nuevo'] == 'EN_SEGUIMIENTO':
                    tarea_cierre_existente = TareaNachec.objects.filter(
                        caso=prestacion.caso,
                        tipo='OTRO',
                        titulo__icontains='Cerrar caso',
                        estado__in=['PENDIENTE', 'EN_PROCESO']
                    ).first()
                    
                    if not tarea_cierre_existente:
                        sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(prestacion.caso.prioridad or 'MEDIA', 2)
                        TareaNachec.objects.create(
                            caso=prestacion.caso,
                            tipo='OTRO',
                            titulo='Cerrar caso - Sin prestaciones activas',
                            descripcion=f"""El caso pasó a EN_SEGUIMIENTO porque no quedan prestaciones activas.

Debe evaluar cierre del caso.

Plan vigente: {prestacion.plan.id}
Última acción: Cancelación de prestación {prestacion.get_tipo_display()}""",
                            asignado_a=prestacion.caso.coordinador or request.user,
                            creado_por=request.user,
                            estado='PENDIENTE',
                            prioridad=prestacion.caso.prioridad or 'MEDIA',
                            fecha_vencimiento=(timezone.now() + timedelta(days=sla_dias)).date()
                        )
        
        messages.info(request, f'Prestación {prestacion.get_tipo_display()} cancelada')
        return redirect('legajos:programa_detalle', pk=2)


# ============================================================================
# PASO 9 - Cierre de Caso
# ============================================================================

@login_required
def cerrar_caso_nachec(request, caso_id):
    """EN_SEGUIMIENTO → CERRADO con validaciones y cierre de plan"""
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from .models_nachec import PrestacionNachec, PlanIntervencionNachec
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Validación 1: Estado EN_SEGUIMIENTO
    if caso.estado != 'EN_SEGUIMIENTO':
        messages.error(request, 'El caso no está en seguimiento')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 2: Control de acceso - solo coordinador o con tarea CIERRE_CASO
    es_coordinador = request.user.id == caso.coordinador_id
    tarea_cierre = TareaNachec.objects.filter(
        caso=caso,
        tipo='OTRO',
        titulo__icontains='Cerrar caso',
        asignado_a=request.user,
        estado__in=['PENDIENTE', 'EN_PROCESO']
    ).first()
    
    if not es_coordinador and not tarea_cierre:
        messages.error(request, 'No tienes permiso para cerrar este caso')
        return HttpResponseForbidden('Acceso denegado: solo coordinador')
    
    # Obtener plan vigente
    plan_vigente = PlanIntervencionNachec.objects.filter(caso=caso, vigente=True).first()
    
    if request.method == 'GET':
        # Validación 3: No debe haber prestaciones activas
        prestaciones_activas = PrestacionNachec.objects.filter(
            plan=plan_vigente,
            estado__in=['PROGRAMADA', 'EN_PROCESO', 'EN_CURSO']
        ).count() if plan_vigente else 0
        
        # Última prestación entregada
        ultima_prestacion = PrestacionNachec.objects.filter(
            caso=caso,
            estado='ENTREGADA'
        ).order_by('-fecha_entregada').first() if plan_vigente else None
        
        # Evaluación
        evaluacion = caso.evaluacion if hasattr(caso, 'evaluacion') else None
        
        # Prestaciones entregadas totales
        prestaciones_entregadas = PrestacionNachec.objects.filter(
            caso=caso,
            estado='ENTREGADA'
        ).count()
        
        return render(request, 'legajos/nachec/modal_cerrar_caso.html', {
            'caso': caso,
            'plan': plan_vigente,
            'evaluacion': evaluacion,
            'prestaciones_activas': prestaciones_activas,
            'ultima_prestacion': ultima_prestacion,
            'prestaciones_entregadas': prestaciones_entregadas,
            'puede_cerrar': prestaciones_activas == 0
        })
    
    # POST: Procesar cierre
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        
        # Validación de concurrencia
        caso.refresh_from_db()
        if caso.estado != 'EN_SEGUIMIENTO':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validación hard: no prestaciones activas
        prestaciones_activas = PrestacionNachec.objects.filter(
            plan=plan_vigente,
            estado__in=['PROGRAMADA', 'EN_PROCESO', 'EN_CURSO']
        ).count() if plan_vigente else 0
        
        if prestaciones_activas > 0:
            messages.error(request, f'No se puede cerrar: existen {prestaciones_activas} prestaciones activas')
            return redirect('legajos:nachec_cerrar_caso', caso_id=caso.id)
        
        # Validaciones de formulario
        motivo_cierre = request.POST.get('motivo_cierre')
        informe_cierre = request.POST.get('informe_cierre', '').strip()
        confirmacion = request.POST.get('confirmacion')
        
        if not motivo_cierre:
            messages.error(request, 'Debe seleccionar un motivo de cierre')
            return redirect('legajos:nachec_cerrar_caso', caso_id=caso.id)
        
        if len(informe_cierre) < 30:
            messages.error(request, 'El informe de cierre debe tener al menos 30 caracteres')
            return redirect('legajos:nachec_cerrar_caso', caso_id=caso.id)
        
        if not confirmacion:
            messages.error(request, 'Debe confirmar el cierre del caso')
            return redirect('legajos:nachec_cerrar_caso', caso_id=caso.id)
        
        with transaction.atomic():
            # 1. Cerrar caso
            estado_anterior = caso.estado
            caso.estado = 'CERRADO'
            caso.fecha_cierre = timezone.now().date()
            caso.motivo_cierre = f"{motivo_cierre}: {informe_cierre}"
            caso.save()
            
            # 2. Desactivar plan vigente
            if plan_vigente:
                plan_vigente.vigente = False
                plan_vigente.save()
            
            # 3. Cancelar tareas abiertas residuales
            tareas_abiertas = TareaNachec.objects.filter(
                caso=caso,
                estado__in=['PENDIENTE', 'EN_PROCESO']
            )
            
            tareas_canceladas = tareas_abiertas.count()
            tareas_abiertas.update(
                estado='CANCELADA',
                resultado=f"Cancelada por cierre de caso: {motivo_cierre}"
            )
            
            # 4. Completar tarea CIERRE_CASO si existe
            if tarea_cierre:
                tarea_cierre.estado = 'COMPLETADA'
                tarea_cierre.fecha_completada = timezone.now()
                tarea_cierre.resultado = f"Caso cerrado: {motivo_cierre}"
                tarea_cierre.save()
            
            # 5. Auditoría final
            prestaciones_entregadas = PrestacionNachec.objects.filter(
                caso=caso,
                estado='ENTREGADA'
            ).count()
            
            score_total = caso.evaluacion.score_total if hasattr(caso, 'evaluacion') else 0
            
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Caso cerrado por {request.user.get_full_name()}
Motivo: {motivo_cierre}
Plan ID: {plan_vigente.id if plan_vigente else 'N/A'}
Prestaciones entregadas: {prestaciones_entregadas}
Score total: {score_total}
Tareas canceladas: {tareas_canceladas}

Informe de cierre:
{informe_cierre}"""
            )
        
        messages.success(request, f'Caso cerrado correctamente. Fecha: {caso.fecha_cierre.strftime("%d/%m/%Y")}')
        return redirect('legajos:programa_detalle', pk=2)


# ============================================================================
# PASO 10 - Reabrir Caso
# ============================================================================

@login_required
def reabrir_caso_nachec(request, caso_id):
    """CERRADO → EN_SEGUIMIENTO/EVALUADO/PLAN_DEFINIDO según tipo de reapertura"""
    from django.http import HttpResponseForbidden
    from django.shortcuts import render
    from .models_nachec import PlanIntervencionNachec, PrestacionNachec
    
    caso = get_object_or_404(CasoNachec, id=caso_id)
    
    # Validación 1: Estado CERRADO
    if caso.estado != 'CERRADO':
        messages.error(request, 'El caso no está cerrado')
        return redirect('legajos:programa_detalle', pk=2)
    
    # Validación 2: Control de acceso - coordinador o superadmin
    es_coordinador = request.user.id == caso.coordinador_id
    es_superadmin = request.user.is_superuser
    
    if not es_coordinador and not es_superadmin:
        messages.error(request, 'No tienes permiso para reabrir este caso')
        return HttpResponseForbidden('Acceso denegado: solo coordinador o superadmin')
    
    if request.method == 'GET':
        # Obtener planes históricos
        planes_historicos = PlanIntervencionNachec.objects.filter(caso=caso).order_by('-creado')
        plan_mas_reciente = planes_historicos.first()
        
        # Prestaciones activas (debería ser 0)
        prestaciones_activas = PrestacionNachec.objects.filter(
            caso=caso,
            estado__in=['PROGRAMADA', 'EN_PROCESO', 'EN_CURSO']
        ).count()
        
        # Evaluación
        evaluacion = caso.evaluacion if hasattr(caso, 'evaluacion') else None
        
        return render(request, 'legajos/nachec/modal_reabrir_caso.html', {
            'caso': caso,
            'plan_mas_reciente': plan_mas_reciente,
            'tiene_plan': planes_historicos.exists(),
            'prestaciones_activas': prestaciones_activas,
            'evaluacion': evaluacion
        })
    
    # POST: Procesar reapertura
    if request.method == 'POST':
        from django.utils import timezone
        from django.db import transaction
        
        # Validación de concurrencia
        caso.refresh_from_db()
        if caso.estado != 'CERRADO':
            messages.error(request, 'El caso ya fue procesado por otro usuario')
            return redirect('legajos:programa_detalle', pk=2)
        
        # Validaciones de formulario
        tipo_reapertura = request.POST.get('tipo_reapertura')
        motivo_reapertura = request.POST.get('motivo_reapertura')
        detalle_reapertura = request.POST.get('detalle_reapertura', '').strip()
        
        if not tipo_reapertura:
            messages.error(request, 'Debe seleccionar tipo de reapertura')
            return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
        
        if not motivo_reapertura:
            messages.error(request, 'Debe seleccionar motivo de reapertura')
            return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
        
        if len(detalle_reapertura) < 30:
            messages.error(request, 'El detalle debe tener al menos 30 caracteres')
            return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
        
        with transaction.atomic():
            estado_anterior = caso.estado
            tareas_creadas = []
            plan_reactivado = None
            
            # MODO ADMINISTRATIVO
            if tipo_reapertura == 'ADMINISTRATIVA':
                caso.estado = 'EN_SEGUIMIENTO'
                caso.fecha_cierre = None
                caso.save()
                
                # Crear tarea REVISION_REAPERTURA
                tarea = TareaNachec.objects.create(
                    caso=caso,
                    tipo='OTRO',
                    titulo='Revisión por reapertura administrativa',
                    descripcion=f"""Caso reabierto administrativamente.

Motivo: {motivo_reapertura}
Detalle: {detalle_reapertura}

Debe revisar documentación y validar información.""",
                    asignado_a=caso.coordinador or request.user,
                    creado_por=request.user,
                    estado='PENDIENTE',
                    prioridad=caso.prioridad or 'MEDIA',
                    fecha_vencimiento=(timezone.now() + timedelta(days=2)).date()
                )
                tareas_creadas.append(tarea.id)
            
            # MODO OPERATIVO
            elif tipo_reapertura == 'OPERATIVA':
                accion_operativa = request.POST.get('accion_operativa')
                
                # Camino A: Reactivar plan existente
                if accion_operativa == 'REACTIVAR_PLAN':
                    plan_mas_reciente = PlanIntervencionNachec.objects.filter(caso=caso).order_by('-creado').first()
                    
                    if not plan_mas_reciente:
                        messages.error(request, 'No existe plan para reactivar. Use "Forzar reevaluación".')
                        return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
                    
                    # Desactivar otros planes y reactivar el más reciente
                    PlanIntervencionNachec.objects.filter(caso=caso, vigente=True).update(vigente=False)
                    plan_mas_reciente.vigente = True
                    plan_mas_reciente.save()
                    plan_reactivado = plan_mas_reciente.id
                    
                    # Volver a PLAN_DEFINIDO para forzar PASO 7 (activación)
                    caso.estado = 'PLAN_DEFINIDO'
                    caso.fecha_cierre = None
                    caso.save()
                    
                    # Crear tarea ACTIVACION_PLAN
                    sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(caso.prioridad or 'MEDIA', 2)
                    tarea = TareaNachec.objects.create(
                        caso=caso,
                        tipo='OTRO',
                        titulo='Activar plan reactivado',
                        descripcion=f"""Caso reabierto operativamente con plan reactivado.

Motivo: {motivo_reapertura}
Detalle: {detalle_reapertura}

Plan ID: {plan_mas_reciente.id}

Debe activar el plan y programar prestaciones.""",
                        asignado_a=caso.coordinador or request.user,
                        creado_por=request.user,
                        estado='PENDIENTE',
                        prioridad=caso.prioridad or 'MEDIA',
                        fecha_vencimiento=(timezone.now() + timedelta(days=sla_dias)).date()
                    )
                    tareas_creadas.append(tarea.id)
                
                # Camino B: Forzar reevaluación
                elif accion_operativa == 'FORZAR_REEVALUACION':
                    # Desactivar planes anteriores
                    PlanIntervencionNachec.objects.filter(caso=caso, vigente=True).update(vigente=False)
                    
                    # Volver a EVALUADO
                    caso.estado = 'EVALUADO'
                    caso.fecha_cierre = None
                    caso.save()
                    
                    # Crear tarea EVALUACION
                    sla_dias = {'URGENTE': 1, 'ALTA': 1, 'MEDIA': 2, 'BAJA': 3}.get(caso.prioridad or 'MEDIA', 2)
                    tarea = TareaNachec.objects.create(
                        caso=caso,
                        tipo='OTRO',
                        titulo='Reevaluar caso reabierto',
                        descripcion=f"""Caso reabierto operativamente para reevaluación.

Motivo: {motivo_reapertura}
Detalle: {detalle_reapertura}

Debe evaluar nuevamente el caso y definir plan de intervención.""",
                        asignado_a=caso.coordinador or request.user,
                        creado_por=request.user,
                        estado='PENDIENTE',
                        prioridad=caso.prioridad or 'MEDIA',
                        fecha_vencimiento=(timezone.now() + timedelta(days=sla_dias)).date()
                    )
                    tareas_creadas.append(tarea.id)
                
                else:
                    messages.error(request, 'Debe seleccionar acción operativa')
                    return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
            
            else:
                messages.error(request, 'Tipo de reapertura inválido')
                return redirect('legajos:nachec_reabrir_caso', caso_id=caso.id)
            
            # Auditoría
            HistorialEstadoCaso.objects.create(
                caso=caso,
                estado_anterior=estado_anterior,
                estado_nuevo=caso.estado,
                usuario=request.user,
                observacion=f"""Caso reabierto por {request.user.get_full_name()}
Tipo: {tipo_reapertura}
Motivo: {motivo_reapertura}
Plan reactivado: {plan_reactivado or 'N/A'}
Tareas creadas: {len(tareas_creadas)}

Detalle:
{detalle_reapertura}"""
            )
        
        messages.success(request, f'Caso reabierto exitosamente. Estado: {caso.get_estado_display()}')
        return redirect('legajos:programa_detalle', pk=2)
