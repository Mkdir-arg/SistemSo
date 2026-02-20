"""
Servicios de lógica de negocio para Sistema NODO - Gestión Programática
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Max

from .models_institucional import (
    DerivacionInstitucional,
    CasoInstitucional,
    # HistorialEstadoCaso,  # TODO: Implementar
    EstadoDerivacion,
    EstadoCaso,
    EstadoGlobal,
    EstadoPrograma
)


class DerivacionService:
    """Servicio para gestión de derivaciones institucionales"""
    
    @staticmethod
    @transaction.atomic
    def aceptar_derivacion(derivacion_id, usuario, responsable_caso=None):
        """
        Acepta una derivación y crea el caso institucional correspondiente.
        
        Validaciones:
        1. Estado global de institución != CERRADO
        2. Estado programático = ACTIVO
        3. Cupo disponible (si aplica)
        4. No existe caso activo previo
        
        Returns:
            tuple: (caso, created) donde created indica si se creó nuevo caso
        """
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)
        
        # Validar estado de derivación
        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})")
        
        # 1. Validar estado global de la institución
        if hasattr(derivacion.institucion, 'legajo_institucional'):
            estado_global = derivacion.institucion.legajo_institucional.estado_global
            if estado_global == EstadoGlobal.CERRADO:
                raise ValidationError("La institución está cerrada globalmente y no puede aceptar derivaciones")
        
        # 2. Validar estado programático
        if derivacion.institucion_programa.estado_programa != EstadoPrograma.ACTIVO:
            raise ValidationError(
                f"El programa está en estado {derivacion.institucion_programa.get_estado_programa_display()} "
                "y no puede aceptar derivaciones"
            )
        
        if not derivacion.institucion_programa.activo:
            raise ValidationError("El programa no está activo en esta institución")
        
        # 3. Validar cupo (si aplica)
        if derivacion.institucion_programa.controlar_cupo:
            casos_activos = CasoInstitucional.objects.filter(
                institucion_programa=derivacion.institucion_programa,
                estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
            ).count()
            
            cupo_maximo = derivacion.institucion_programa.cupo_maximo
            
            if casos_activos >= cupo_maximo:
                if not derivacion.institucion_programa.permite_sobrecupo:
                    raise ValidationError(
                        f"Cupo lleno ({casos_activos}/{cupo_maximo}). "
                        "No se permite sobrecupo en este programa."
                    )
        
        # 4. Buscar caso existente activo
        caso_existente = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).first()
        
        # Si existe caso activo → ACEPTADA_UNIFICADA
        if caso_existente:
            derivacion.estado = EstadoDerivacion.ACEPTADA_UNIFICADA
            derivacion.caso_creado = caso_existente
            derivacion.respondido_por = usuario
            derivacion.fecha_respuesta = timezone.now()
            derivacion.respuesta = f"Unificada con caso existente {caso_existente.codigo}"
            derivacion.save()
            
            # TODO: Registrar en historial del caso cuando exista HistorialEstadoCaso
            # HistorialEstadoCaso.objects.create(
            #     caso=caso_existente,
            #     estado_anterior=caso_existente.estado,
            #     estado_nuevo=caso_existente.estado,
            #     usuario=usuario,
            #     observacion=f"Derivación unificada (ID: {derivacion.id})"
            # )
            
            return caso_existente, False
        
        # Si NO existe → Crear nuevo caso
        # Calcular versión
        ultima_version = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa
        ).aggregate(Max('version'))['version__max'] or 0
        
        caso = CasoInstitucional.objects.create(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            version=ultima_version + 1,
            estado=EstadoCaso.ACTIVO,
            responsable_caso=responsable_caso or usuario,
            derivacion_origen=derivacion
        )
        
        # Actualizar derivación
        derivacion.estado = EstadoDerivacion.ACEPTADA
        derivacion.caso_creado = caso
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.respuesta = f"Caso creado: {caso.codigo}"
        derivacion.save()
        
        # TODO: Registrar en historial cuando exista HistorialEstadoCaso
        # HistorialEstadoCaso.objects.create(
        #     caso=caso,
        #     estado_anterior='',
        #     estado_nuevo=EstadoCaso.ACTIVO,
        #     usuario=usuario,
        #     observacion=f"Caso creado por aceptación de derivación (ID: {derivacion.id})"
        # )
        
        return caso, True
    
    @staticmethod
    @transaction.atomic
    def rechazar_derivacion(derivacion_id, usuario, motivo_rechazo):
        """
        Rechaza una derivación institucional.
        
        Args:
            derivacion_id: ID de la derivación
            usuario: Usuario que rechaza
            motivo_rechazo: Motivo del rechazo
        """
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)
        
        # Validar estado
        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})")
        
        # Actualizar derivación
        derivacion.estado = EstadoDerivacion.RECHAZADA
        derivacion.respuesta = motivo_rechazo
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.save()


class CasoService:
    """Servicio para gestión de casos institucionales"""
    
    @staticmethod
    @transaction.atomic
    def cambiar_estado_caso(caso_id, nuevo_estado, usuario, observacion='', motivo_cierre=''):
        """
        Cambia el estado de un caso institucional.
        
        Args:
            caso_id: ID del caso
            nuevo_estado: Nuevo estado (usar EstadoCaso)
            usuario: Usuario que realiza el cambio
            observacion: Observación del cambio
            motivo_cierre: Motivo de cierre (si aplica)
        """
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)
        
        estado_anterior = caso.estado
        
        # Validar transición
        if estado_anterior == nuevo_estado:
            raise ValidationError("El caso ya está en ese estado")
        
        # Actualizar caso
        caso.estado = nuevo_estado
        
        if nuevo_estado in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            caso.fecha_cierre = timezone.now().date()
            if motivo_cierre:
                caso.motivo_cierre = motivo_cierre
        
        if observacion:
            if caso.notas:
                caso.notas += f"\n\n{observacion}"
            else:
                caso.notas = observacion
        
        caso.save()
        
        # TODO: Registrar en historial cuando exista HistorialEstadoCaso
        # HistorialEstadoCaso.objects.create(
        #     caso=caso,
        #     estado_anterior=estado_anterior,
        #     estado_nuevo=nuevo_estado,
        #     usuario=usuario,
        #     observacion=observacion or f"Cambio de estado: {estado_anterior} → {nuevo_estado}"
        # )
        
        return caso
    
    @staticmethod
    @transaction.atomic
    def reabrir_caso(caso_id, usuario, observacion=''):
        """
        Reabre un caso cerrado o egresado.
        
        Args:
            caso_id: ID del caso
            usuario: Usuario que reabre
            observacion: Motivo de reapertura
        """
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)
        
        if caso.estado not in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            raise ValidationError("Solo se pueden reabrir casos cerrados o egresados")
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.ACTIVO
        caso.fecha_cierre = None
        
        if observacion:
            if caso.notas:
                caso.notas += f"\n\n[REAPERTURA] {observacion}"
            else:
                caso.notas = f"[REAPERTURA] {observacion}"
        
        caso.save()
        
        # TODO: Registrar en historial cuando exista HistorialEstadoCaso
        # HistorialEstadoCaso.objects.create(
        #     caso=caso,
        #     estado_anterior=estado_anterior,
        #     estado_nuevo=EstadoCaso.ACTIVO,
        #     usuario=usuario,
        #     observacion=observacion or "Caso reabierto"
        # )
        
        return caso
