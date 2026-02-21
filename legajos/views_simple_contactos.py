from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import LegajoAtencion, Ciudadano
from datetime import datetime
try:
    from .models_contactos import VinculoFamiliar
except ImportError:
    VinculoFamiliar = None

def red_contactos_simple(request, legajo_id):
    """Vista simple para red de contactos"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    context = {
        'legajo': legajo,
        'ciudadano': legajo.ciudadano,
    }
    
    return render(request, 'legajos/red_contactos_simple.html', context)



def dashboard_contactos_simple(request):
    """Dashboard simple de contactos"""
    context = {
        'titulo': 'Dashboard de Contactos',
    }
    
    return render(request, 'legajos/dashboard_contactos_simple.html', context)

def historial_contactos_simple(request, legajo_id):
    """Vista simple para historial de contactos"""
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    
    context = {
        'legajo': legajo,
        'ciudadano': legajo.ciudadano,
    }
    
    return render(request, 'legajos/historial_contactos_simple.html', context)

def actividades_ciudadano_api(request, ciudadano_id):
    """API para obtener todas las actividades de un ciudadano"""
    try:
        ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
        legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano).select_related('dispositivo', 'responsable')
        
        actividades = []
        
        # Actividades básicas de legajos
        for legajo in legajos:
            # Apertura de acompañamiento
            if legajo.fecha_apertura:
                actividades.append({
                    'fecha_hora': legajo.fecha_apertura.isoformat(),
                    'tipo': 'APERTURA',
                    'descripcion': f'Acompañamiento abierto en {legajo.dispositivo.nombre if legajo.dispositivo else "Dispositivo no especificado"}',
                    'usuario_nombre': legajo.responsable.get_full_name() if legajo.responsable else 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
            
            # Cierre de acompañamiento
            if hasattr(legajo, 'fecha_cierre') and legajo.fecha_cierre:
                actividades.append({
                    'fecha_hora': legajo.fecha_cierre.isoformat(),
                    'tipo': 'CIERRE',
                    'descripcion': 'Acompañamiento cerrado',
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
            
            # Seguimientos
            from .models import SeguimientoContacto
            seguimientos = SeguimientoContacto.objects.filter(legajo=legajo).select_related('profesional__usuario')
            for seg in seguimientos:
                actividades.append({
                    'fecha_hora': seg.creado.isoformat(),
                    'tipo': 'SEGUIMIENTO',
                    'descripcion': f'{seg.get_tipo_display()}: {seg.descripcion[:100] if seg.descripcion else "Sin descripción"}',
                    'usuario_nombre': seg.profesional.usuario.get_full_name() if seg.profesional and seg.profesional.usuario else 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
            
            # Evaluaciones
            from .models import EvaluacionInicial
            try:
                if hasattr(legajo, 'evaluacion'):
                    eval = legajo.evaluacion
                    actividades.append({
                        'fecha_hora': eval.creado.isoformat(),
                        'tipo': 'EVALUACION',
                        'descripcion': f'Evaluación inicial realizada - Riesgo: {eval.nivel_riesgo if hasattr(eval, "nivel_riesgo") else "No especificado"}',
                        'usuario_nombre': 'Sistema',
                        'legajo_id': str(legajo.id),
                        'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                    })
            except:
                pass
            
            # Planes de intervención
            from .models import PlanIntervencion
            planes = PlanIntervencion.objects.filter(legajo=legajo).select_related('profesional__usuario')
            for plan in planes:
                actividades.append({
                    'fecha_hora': plan.creado.isoformat(),
                    'tipo': 'PLAN',
                    'descripcion': f'Plan de intervención creado - Objetivos: {plan.objetivos[:100] if plan.objetivos else "Sin objetivos"}',
                    'usuario_nombre': plan.profesional.usuario.get_full_name() if plan.profesional and plan.profesional.usuario else 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
            
            # Derivaciones
            from .models import Derivacion
            derivaciones = Derivacion.objects.filter(legajo=legajo).select_related('destino')
            for der in derivaciones:
                actividades.append({
                    'fecha_hora': der.creado.isoformat(),
                    'tipo': 'DERIVACION',
                    'descripcion': f'Derivación a {der.destino.nombre if der.destino else "destino no especificado"} - Estado: {der.get_estado_display()}',
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
            
            # Eventos críticos
            from .models import EventoCritico
            eventos = EventoCritico.objects.filter(legajo=legajo)
            for evento in eventos:
                actividades.append({
                    'fecha_hora': evento.creado.isoformat(),
                    'tipo': 'EVENTO',
                    'descripcion': f'Evento crítico: {evento.get_tipo_display()} - {evento.descripcion[:100] if evento.descripcion else ""}',
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id)
                })
        
        # Vínculos familiares
        try:
            vinculos = VinculoFamiliar.objects.filter(ciudadano_principal=ciudadano)
            for vinculo in vinculos:
                actividades.append({
                    'fecha_hora': vinculo.creado.isoformat() if hasattr(vinculo, 'creado') else datetime.now().isoformat(),
                    'tipo': 'VINCULO',
                    'descripcion': f'Vínculo agregado: {vinculo.get_tipo_vinculo_display() if hasattr(vinculo, "get_tipo_vinculo_display") else vinculo.tipo_vinculo}',
                    'usuario_nombre': 'Sistema',
                    'legajo_id': '-',
                    'legajo_codigo': 'General'
                })
        except Exception as e:
            print(f"Error cargando vínculos: {e}")
        
        # Ordenar por fecha descendente
        actividades.sort(key=lambda x: x['fecha_hora'] or '', reverse=True)
        
        return JsonResponse({
            'results': actividades[:50],  # Limitar a 50 registros
            'count': len(actividades)
        })
        
    except Exception as e:
        print(f"Error en actividades_ciudadano_api: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'results': [],
            'count': 0,
            'error': str(e)
        })

def subir_archivos_ciudadano(request, ciudadano_id):
    """Vista para subir archivos a un ciudadano"""
    if request.method == 'POST':
        try:
            ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
            
            archivos = request.FILES.getlist('archivo')
            etiqueta = request.POST.get('etiqueta', '')
            
            if not archivos:
                return JsonResponse({'success': False, 'error': 'No se seleccionaron archivos'})
            
            archivos_subidos = []
            
            for archivo in archivos:
                # Validar tamaño (10MB máximo)
                if archivo.size > 10 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': f'El archivo {archivo.name} es muy grande (máx. 10MB)'})
                
                # Validar extensión
                extensiones_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
                nombre_archivo = archivo.name.lower()
                if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                    return JsonResponse({'success': False, 'error': f'Formato no permitido: {archivo.name}'})
                
                # Crear adjunto usando el modelo genérico
                from django.contrib.contenttypes.models import ContentType
                from .models import Adjunto
                
                content_type = ContentType.objects.get_for_model(Ciudadano)
                adjunto = Adjunto.objects.create(
                    content_type=content_type,
                    object_id=ciudadano.id,
                    archivo=archivo,
                    etiqueta=etiqueta or archivo.name
                )
                
                archivos_subidos.append({
                    'id': adjunto.id,
                    'nombre': archivo.name,
                    'etiqueta': adjunto.etiqueta
                })
            
            return JsonResponse({
                'success': True,
                'archivos': archivos_subidos,
                'mensaje': f'{len(archivos_subidos)} archivo(s) subido(s) exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def subir_archivos_legajo(request, legajo_id):
    """Vista para subir archivos a un legajo"""
    if request.method == 'POST':
        try:
            legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
            
            archivos = request.FILES.getlist('archivo')
            etiqueta = request.POST.get('etiqueta', '')
            
            if not archivos:
                return JsonResponse({'success': False, 'error': 'No se seleccionaron archivos'})
            
            archivos_subidos = []
            
            for archivo in archivos:
                # Validar tamaño (10MB máximo)
                if archivo.size > 10 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': f'El archivo {archivo.name} es muy grande (máx. 10MB)'})
                
                # Validar extensión
                extensiones_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
                nombre_archivo = archivo.name.lower()
                if not any(nombre_archivo.endswith(ext) for ext in extensiones_permitidas):
                    return JsonResponse({'success': False, 'error': f'Formato no permitido: {archivo.name}'})
                
                # Crear adjunto usando el modelo genérico
                from django.contrib.contenttypes.models import ContentType
                from .models import Adjunto
                
                content_type = ContentType.objects.get_for_model(LegajoAtencion)
                adjunto = Adjunto.objects.create(
                    content_type=content_type,
                    object_id=legajo.id,
                    archivo=archivo,
                    etiqueta=etiqueta or archivo.name
                )
                
                archivos_subidos.append({
                    'id': adjunto.id,
                    'nombre': archivo.name,
                    'etiqueta': adjunto.etiqueta
                })
            
            return JsonResponse({
                'success': True,
                'archivos': archivos_subidos,
                'mensaje': f'{len(archivos_subidos)} archivo(s) subido(s) exitosamente'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def archivos_ciudadano_api(request, ciudadano_id):
    """API para obtener todos los archivos de un ciudadano"""
    try:
        ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
        legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano)
        
        from django.contrib.contenttypes.models import ContentType
        from .models import Adjunto
        
        # Obtener archivos del ciudadano y de sus legajos
        ciudadano_content_type = ContentType.objects.get_for_model(Ciudadano)
        legajo_content_type = ContentType.objects.get_for_model(LegajoAtencion)
        
        archivos_ciudadano = Adjunto.objects.filter(
            content_type=ciudadano_content_type,
            object_id=ciudadano_id
        )
        
        archivos_legajos = Adjunto.objects.filter(
            content_type=legajo_content_type,
            object_id__in=[str(legajo.id) for legajo in legajos]
        )
        
        # Combinar ambos querysets
        from django.db.models import Q
        archivos = Adjunto.objects.filter(
            Q(content_type=ciudadano_content_type, object_id=ciudadano_id) |
            Q(content_type=legajo_content_type, object_id__in=[str(legajo.id) for legajo in legajos])
        ).order_by('-creado')
        
        archivos_data = []
        for archivo in archivos:
            if archivo.content_type.model == 'ciudadano':
                # Archivo del ciudadano
                archivos_data.append({
                    'id': archivo.id,
                    'nombre': archivo.archivo.name.split('/')[-1],
                    'etiqueta': archivo.etiqueta,
                    'url': archivo.archivo.url,
                    'tamano': archivo.archivo.size,
                    'fecha_subida': archivo.creado.isoformat(),
                    'legajo_id': '-',
                    'legajo_codigo': 'Ciudadano',
                    'tipo_origen': 'ciudadano'
                })
            else:
                # Archivo del legajo
                try:
                    legajo = LegajoAtencion.objects.get(id=archivo.object_id)
                    archivos_data.append({
                        'id': archivo.id,
                        'nombre': archivo.archivo.name.split('/')[-1],
                        'etiqueta': archivo.etiqueta,
                        'url': archivo.archivo.url,
                        'tamano': archivo.archivo.size,
                        'fecha_subida': archivo.creado.isoformat(),
                        'legajo_id': str(legajo.id),
                        'legajo_codigo': str(legajo.codigo)[:12] + '...' if legajo.codigo else str(legajo.id),
                        'tipo_origen': 'legajo'
                    })
                except LegajoAtencion.DoesNotExist:
                    continue
        
        return JsonResponse({
            'results': archivos_data,
            'count': len(archivos_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'results': [],
            'count': 0,
            'error': str(e)
        })

def eliminar_archivo(request, archivo_id):
    """Vista para eliminar un archivo"""
    if request.method == 'DELETE':
        try:
            from .models import Adjunto
            archivo = get_object_or_404(Adjunto, id=archivo_id)
            archivo.delete()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def alertas_ciudadano_api(request, ciudadano_id):
    """API para obtener alertas de un ciudadano"""
    try:
        from .services_alertas import AlertasService
        
        # Generar alertas actualizadas
        AlertasService.generar_alertas_ciudadano(ciudadano_id)
        
        # Obtener alertas activas
        alertas = AlertasService.obtener_alertas_ciudadano(ciudadano_id)
        
        alertas_data = []
        for alerta in alertas:
            alertas_data.append({
                'id': alerta.id,
                'tipo': alerta.tipo,
                'tipo_display': alerta.get_tipo_display(),
                'prioridad': alerta.prioridad,
                'mensaje': alerta.mensaje,
                'color_css': alerta.color_css,
                'fecha_creacion': alerta.creado.isoformat(),
                'legajo_id': str(alerta.legajo.id) if alerta.legajo else None
            })
        
        return JsonResponse({
            'results': alertas_data,
            'count': len(alertas_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'results': [],
            'count': 0,
            'error': str(e)
        })

def cerrar_alerta_api(request, alerta_id):
    """API para cerrar una alerta"""
    if request.method == 'POST':
        try:
            from .services_alertas import AlertasService
            
            success = AlertasService.cerrar_alerta(alerta_id, request.user)
            
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Alerta no encontrada'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def prediccion_riesgo_api(request, ciudadano_id):
    """API para obtener predicción de riesgo con IA"""
    try:
        from .ml_predictor import RiskPredictor
        
        ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
        prediccion = RiskPredictor.obtener_prediccion_completa(ciudadano)
        
        return JsonResponse(prediccion)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'abandono': {'score': 0, 'nivel': 'BAJO', 'factores': []},
            'evento_critico': {'score': 0, 'nivel': 'BAJO', 'factores': []},
            'recomendaciones': []
        })

def evolucion_legajo_api(request, legajo_id):
    """API para obtener datos de evolución de un legajo"""
    try:
        from .models import SeguimientoContacto, PlanIntervencion, Objetivo, EvaluacionInicial, Derivacion, EventoCritico
        
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        
        # Total de seguimientos
        total_seguimientos = SeguimientoContacto.objects.filter(legajo=legajo).count()
        
        # Adherencia promedio
        seguimientos_con_adherencia = SeguimientoContacto.objects.filter(
            legajo=legajo,
            adherencia__isnull=False
        )
        
        adherencia_promedio = None
        if seguimientos_con_adherencia.exists():
            adherencia_map = {'ADECUADA': 100, 'PARCIAL': 50, 'NULA': 0}
            total = 0
            count = 0
            for seg in seguimientos_con_adherencia:
                total += adherencia_map.get(seg.adherencia, 0)
                count += 1
            adherencia_promedio = round(total / count) if count > 0 else None
        
        # Objetivos (etapas del plan vigente)
        plan_vigente = PlanIntervencion.objects.filter(legajo=legajo, vigente=True).first()
        objetivos_totales = 0
        objetivos_cumplidos = 0
        
        if plan_vigente and plan_vigente.actividades:
            objetivos_totales = len(plan_vigente.actividades)
            objetivos_cumplidos = sum(1 for act in plan_vigente.actividades if act.get('completada', False))
        
        # Hitos del tratamiento
        hitos = []
        
        # Apertura
        hitos.append({
            'tipo': 'APERTURA',
            'titulo': 'Apertura de Acompañamiento',
            'fecha': legajo.fecha_apertura.isoformat()
        })
        
        # Evaluación
        if hasattr(legajo, 'evaluacion'):
            hitos.append({
                'tipo': 'EVALUACION',
                'titulo': 'Evaluación Inicial',
                'fecha': legajo.evaluacion.creado.isoformat()
            })
        
        # Plan vigente
        plan_vigente = PlanIntervencion.objects.filter(legajo=legajo, vigente=True).first()
        if plan_vigente:
            hitos.append({
                'tipo': 'PLAN',
                'titulo': 'Plan de Intervención Activo',
                'fecha': plan_vigente.creado.isoformat()
            })
        
        # Último seguimiento
        ultimo_seguimiento = SeguimientoContacto.objects.filter(legajo=legajo).order_by('-creado').first()
        if ultimo_seguimiento:
            hitos.append({
                'tipo': 'SEGUIMIENTO',
                'titulo': f'Último Seguimiento - {ultimo_seguimiento.get_tipo_display()}',
                'fecha': ultimo_seguimiento.creado.isoformat()
            })
        
        # Derivaciones
        derivacion_reciente = Derivacion.objects.filter(legajo=legajo).order_by('-creado').first()
        if derivacion_reciente:
            hitos.append({
                'tipo': 'DERIVACION',
                'titulo': f'Derivación a {derivacion_reciente.destino.nombre}',
                'fecha': derivacion_reciente.creado.isoformat()
            })
        
        # Eventos críticos
        evento_reciente = EventoCritico.objects.filter(legajo=legajo).order_by('-creado').first()
        if evento_reciente:
            hitos.append({
                'tipo': 'EVENTO',
                'titulo': f'Evento: {evento_reciente.get_tipo_display()}',
                'fecha': evento_reciente.creado.isoformat()
            })
        
        # Cierre
        if legajo.fecha_cierre:
            hitos.append({
                'tipo': 'CIERRE',
                'titulo': 'Cierre de Acompañamiento',
                'fecha': legajo.fecha_cierre.isoformat()
            })
        
        # Ordenar por fecha
        hitos.sort(key=lambda x: x['fecha'])
        
        return JsonResponse({
            'total_seguimientos': total_seguimientos,
            'adherencia_promedio': adherencia_promedio,
            'objetivos_totales': objetivos_totales,
            'objetivos_cumplidos': objetivos_cumplidos,
            'hitos': hitos
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'total_seguimientos': 0,
            'adherencia_promedio': None,
            'objetivos_totales': 0,
            'objetivos_cumplidos': 0,
            'hitos': []
        })

def timeline_ciudadano_api(request, ciudadano_id):
    """API para obtener línea temporal de eventos del ciudadano"""
    try:
        ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
        legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano).select_related('dispositivo', 'responsable')
        
        eventos = []
        
        for legajo in legajos:
            # Apertura de legajo
            eventos.append({
                'fecha': legajo.fecha_apertura.isoformat(),
                'tipo': 'APERTURA',
                'titulo': 'Apertura de Acompañamiento',
                'descripcion': f'Acompañamiento iniciado en {legajo.dispositivo.nombre if legajo.dispositivo else "dispositivo no especificado"}',
                'legajo_id': str(legajo.id)
            })
            
            # Evaluación inicial
            try:
                if hasattr(legajo, 'evaluacion'):
                    eval = legajo.evaluacion
                    eventos.append({
                        'fecha': eval.creado.isoformat(),
                        'tipo': 'EVALUACION',
                        'titulo': 'Evaluación Inicial',
                        'descripcion': f'Evaluación realizada - Nivel de riesgo: {legajo.get_nivel_riesgo_display()}',
                        'legajo_id': str(legajo.id)
                    })
            except:
                pass
            
            # Planes de intervención
            from .models import PlanIntervencion
            planes = PlanIntervencion.objects.filter(legajo=legajo, vigente=True)
            for plan in planes:
                eventos.append({
                    'fecha': plan.creado.isoformat(),
                    'tipo': 'PLAN',
                    'titulo': 'Plan de Intervención',
                    'descripcion': 'Plan de intervención creado y activado',
                    'legajo_id': str(legajo.id)
                })
            
            # Seguimientos importantes (solo los primeros 3)
            from .models import SeguimientoContacto
            seguimientos = SeguimientoContacto.objects.filter(legajo=legajo).order_by('-creado')[:3]
            for seg in seguimientos:
                eventos.append({
                    'fecha': seg.creado.isoformat(),
                    'tipo': 'SEGUIMIENTO',
                    'titulo': f'Seguimiento - {seg.get_tipo_display()}',
                    'descripcion': seg.descripcion[:150] if seg.descripcion else 'Sin descripción',
                    'legajo_id': str(legajo.id)
                })
            
            # Derivaciones
            from .models import Derivacion
            derivaciones = Derivacion.objects.filter(legajo=legajo).select_related('destino')
            for der in derivaciones:
                eventos.append({
                    'fecha': der.creado.isoformat(),
                    'tipo': 'DERIVACION',
                    'titulo': 'Derivación',
                    'descripcion': f'Derivado a {der.destino.nombre if der.destino else "destino no especificado"} - {der.get_estado_display()}',
                    'legajo_id': str(legajo.id)
                })
            
            # Eventos críticos
            from .models import EventoCritico
            eventos_criticos = EventoCritico.objects.filter(legajo=legajo)
            for evento in eventos_criticos:
                eventos.append({
                    'fecha': evento.creado.isoformat(),
                    'tipo': 'EVENTO',
                    'titulo': f'Evento Crítico - {evento.get_tipo_display()}',
                    'descripcion': evento.detalle[:150] if evento.detalle else '',
                    'legajo_id': str(legajo.id)
                })
            
            # Cierre de legajo
            if hasattr(legajo, 'fecha_cierre') and legajo.fecha_cierre:
                eventos.append({
                    'fecha': legajo.fecha_cierre.isoformat(),
                    'tipo': 'CIERRE',
                    'titulo': 'Cierre de Acompañamiento',
                    'descripcion': f'Acompañamiento cerrado - Estado: {legajo.get_estado_display()}',
                    'legajo_id': str(legajo.id)
                })
        
        # Vínculos familiares
        try:
            vinculos = VinculoFamiliar.objects.filter(ciudadano_principal=ciudadano)
            for vinculo in vinculos:
                eventos.append({
                    'fecha': vinculo.creado.isoformat() if hasattr(vinculo, 'creado') else datetime.now().isoformat(),
                    'tipo': 'VINCULO',
                    'titulo': 'Vínculo Familiar',
                    'descripcion': f'Vínculo agregado: {vinculo.get_tipo_vinculo_display() if hasattr(vinculo, "get_tipo_vinculo_display") else vinculo.tipo_vinculo}',
                    'legajo_id': None
                })
        except:
            pass
        
        # Alertas importantes
        try:
            from .models import AlertaCiudadano
            alertas = AlertaCiudadano.objects.filter(
                ciudadano=ciudadano,
                prioridad__in=['CRITICA', 'ALTA']
            ).order_by('-creado')[:5]
            
            for alerta in alertas:
                eventos.append({
                    'fecha': alerta.creado.isoformat(),
                    'tipo': 'ALERTA',
                    'titulo': f'Alerta - {alerta.get_tipo_display()}',
                    'descripcion': alerta.mensaje,
                    'legajo_id': str(alerta.legajo.id) if alerta.legajo else None
                })
        except:
            pass
        
        # Ordenar por fecha descendente
        eventos.sort(key=lambda x: x['fecha'], reverse=True)
        
        return JsonResponse({
            'eventos': eventos[:30],  # Limitar a 30 eventos más recientes
            'count': len(eventos)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'eventos': [],
            'count': 0,
            'error': str(e)
        })


@login_required
def archivos_legajo_api(request, legajo_id):
    """API para obtener archivos de un legajo"""
    try:
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        from django.contrib.contenttypes.models import ContentType
        from .models import Adjunto
        
        content_type = ContentType.objects.get_for_model(LegajoAtencion)
        archivos = Adjunto.objects.filter(
            content_type=content_type,
            object_id=legajo.id
        ).order_by('-creado')
        
        archivos_data = [{
            'id': archivo.id,
            'nombre': archivo.archivo.name.split('/')[-1],
            'etiqueta': archivo.etiqueta,
            'url': archivo.archivo.url,
            'fecha': archivo.creado.strftime('%d/%m/%Y %H:%M')
        } for archivo in archivos]
        
        return JsonResponse({'success': True, 'archivos': archivos_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
