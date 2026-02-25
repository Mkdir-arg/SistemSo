"""
Servicios para gestión de transiciones de estado - Programa Ñachec
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from .models_nachec import (
    CasoNachec, EstadoCaso, HistorialEstadoCaso,
    TareaNachec, TipoTarea, EstadoTarea, PrioridadCaso
)


class ServicioTransicionNachec:
    """Servicio para manejar transiciones de estado del caso"""
    
    # Transiciones permitidas
    TRANSICIONES_PERMITIDAS = {
        EstadoCaso.DERIVADO: [EstadoCaso.EN_REVISION, EstadoCaso.RECHAZADO],
        EstadoCaso.EN_REVISION: [EstadoCaso.A_ASIGNAR, EstadoCaso.RECHAZADO],
        EstadoCaso.A_ASIGNAR: [EstadoCaso.ASIGNADO],
        EstadoCaso.ASIGNADO: [EstadoCaso.EN_RELEVAMIENTO, EstadoCaso.SUSPENDIDO],
        EstadoCaso.EN_RELEVAMIENTO: [EstadoCaso.EVALUADO, EstadoCaso.SUSPENDIDO],
        EstadoCaso.EVALUADO: [EstadoCaso.PLAN_DEFINIDO, EstadoCaso.EN_RELEVAMIENTO, EstadoCaso.SUSPENDIDO],
        EstadoCaso.PLAN_DEFINIDO: [EstadoCaso.EN_EJECUCION, EstadoCaso.SUSPENDIDO],
        EstadoCaso.EN_EJECUCION: [EstadoCaso.EN_SEGUIMIENTO, EstadoCaso.SUSPENDIDO],
        EstadoCaso.EN_SEGUIMIENTO: [EstadoCaso.CERRADO, EstadoCaso.SUSPENDIDO],
        EstadoCaso.SUSPENDIDO: [
            EstadoCaso.ASIGNADO, EstadoCaso.EN_RELEVAMIENTO, EstadoCaso.EVALUADO,
            EstadoCaso.PLAN_DEFINIDO, EstadoCaso.EN_EJECUCION, EstadoCaso.EN_SEGUIMIENTO
        ],
    }
    
    @classmethod
    def validar_transicion(cls, caso, nuevo_estado):
        """Valida si la transición es permitida"""
        estados_permitidos = cls.TRANSICIONES_PERMITIDAS.get(caso.estado, [])
        if nuevo_estado not in estados_permitidos:
            raise ValidationError(
                f"No se puede cambiar de {caso.get_estado_display()} a {EstadoCaso(nuevo_estado).label}"
            )
    
    @classmethod
    def registrar_historial(cls, caso, estado_anterior, estado_nuevo, usuario, observacion=""):
        """Registra el cambio de estado en el historial"""
        HistorialEstadoCaso.objects.create(
            caso=caso,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario=usuario,
            observacion=observacion
        )
    
    @classmethod
    @transaction.atomic
    def tomar_caso(cls, caso, usuario):
        """DERIVADO → EN_REVISION"""
        cls.validar_transicion(caso, EstadoCaso.EN_REVISION)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.EN_REVISION
        caso.operador_admision = usuario
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, "Caso tomado por operador")
        return caso
    
    @classmethod
    @transaction.atomic
    def rechazar_caso(cls, caso, usuario, motivo):
        """DERIVADO/EN_REVISION → RECHAZADO"""
        if not motivo:
            raise ValidationError("El motivo de rechazo es obligatorio")
        
        cls.validar_transicion(caso, EstadoCaso.RECHAZADO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.RECHAZADO
        caso.motivo_rechazo = motivo
        caso.fecha_cierre = timezone.now().date()
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, f"Rechazado: {motivo}")
        return caso
    
    @classmethod
    @transaction.atomic
    def enviar_a_asignacion(cls, caso, usuario):
        """EN_REVISION → A_ASIGNAR"""
        # Validaciones
        if not caso.ciudadano_titular:
            raise ValidationError("Debe existir un ciudadano titular vinculado")
        
        if not caso.municipio or not caso.localidad:
            raise ValidationError("Debe completar municipio y localidad")
        
        cls.validar_transicion(caso, EstadoCaso.A_ASIGNAR)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.A_ASIGNAR
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, "Enviado a asignación")
        return caso
    
    @classmethod
    @transaction.atomic
    def asignar_territorial(cls, caso, coordinador, territorial, fecha_limite_relevamiento=None):
        """A_ASIGNAR → ASIGNADO"""
        if not territorial:
            raise ValidationError("Debe seleccionar un territorial")
        
        cls.validar_transicion(caso, EstadoCaso.ASIGNADO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.ASIGNADO
        caso.coordinador = coordinador
        caso.territorial = territorial
        caso.fecha_asignacion = timezone.now().date()
        
        # Calcular SLA si no se proporciona
        if not fecha_limite_relevamiento:
            fecha_limite_relevamiento = timezone.now().date() + timedelta(days=7)
        caso.sla_relevamiento = fecha_limite_relevamiento
        
        caso.save()
        
        # Crear tarea de relevamiento
        TareaNachec.objects.create(
            caso=caso,
            tipo=TipoTarea.RELEVAMIENTO,
            titulo="Relevamiento sociofamiliar inicial",
            descripcion="Realizar relevamiento completo de la situación sociofamiliar",
            asignado_a=territorial,
            creado_por=coordinador,
            estado=EstadoTarea.PENDIENTE,
            prioridad=caso.prioridad,
            fecha_vencimiento=fecha_limite_relevamiento
        )
        
        cls.registrar_historial(
            caso, estado_anterior, caso.estado, coordinador,
            f"Asignado a {territorial.get_full_name()}"
        )
        return caso
    
    @classmethod
    @transaction.atomic
    def iniciar_relevamiento(cls, caso, territorial):
        """ASIGNADO → EN_RELEVAMIENTO"""
        if caso.territorial != territorial:
            raise ValidationError("Solo el territorial asignado puede iniciar el relevamiento")
        
        cls.validar_transicion(caso, EstadoCaso.EN_RELEVAMIENTO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.EN_RELEVAMIENTO
        caso.fecha_relevamiento = timezone.now().date()
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, territorial, "Relevamiento iniciado")
        return caso
    
    @classmethod
    @transaction.atomic
    def finalizar_relevamiento(cls, caso, territorial):
        """EN_RELEVAMIENTO → EVALUADO"""
        # Validar que existe relevamiento completo
        if not hasattr(caso, 'relevamiento'):
            raise ValidationError("No existe relevamiento asociado")
        
        if not caso.relevamiento.completado:
            raise ValidationError("El relevamiento debe estar completado")
        
        cls.validar_transicion(caso, EstadoCaso.EVALUADO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.EVALUADO
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, territorial, "Relevamiento finalizado")
        return caso
    
    @classmethod
    @transaction.atomic
    def confirmar_evaluacion(cls, caso, evaluador):
        """EVALUADO → PLAN_DEFINIDO"""
        # Validar que existe evaluación
        if not hasattr(caso, 'evaluacion'):
            raise ValidationError("No existe evaluación de vulnerabilidad")
        
        if not caso.evaluacion.categoria_final:
            raise ValidationError("Debe completar la categoría final de vulnerabilidad")
        
        cls.validar_transicion(caso, EstadoCaso.PLAN_DEFINIDO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.PLAN_DEFINIDO
        caso.fecha_evaluacion = timezone.now().date()
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, evaluador, "Evaluación confirmada")
        return caso
    
    @classmethod
    @transaction.atomic
    def activar_plan(cls, caso, referente):
        """PLAN_DEFINIDO → EN_EJECUCION"""
        # Validar que existe plan vigente
        plan_vigente = caso.planes.filter(vigente=True).first()
        if not plan_vigente:
            raise ValidationError("No existe plan de intervención vigente")
        
        cls.validar_transicion(caso, EstadoCaso.EN_EJECUCION)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.EN_EJECUCION
        caso.referente_programa = referente
        
        # Marcar fecha de activación del plan
        plan_vigente.fecha_activacion = timezone.now()
        plan_vigente.save()
        
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, referente, "Plan activado")
        return caso
    
    @classmethod
    @transaction.atomic
    def pasar_a_seguimiento(cls, caso, usuario):
        """EN_EJECUCION → EN_SEGUIMIENTO"""
        cls.validar_transicion(caso, EstadoCaso.EN_SEGUIMIENTO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.EN_SEGUIMIENTO
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, "Pasado a seguimiento")
        return caso
    
    @classmethod
    @transaction.atomic
    def cerrar_caso(cls, caso, usuario, motivo_cierre):
        """EN_SEGUIMIENTO → CERRADO"""
        if not motivo_cierre:
            raise ValidationError("El motivo de cierre es obligatorio")
        
        cls.validar_transicion(caso, EstadoCaso.CERRADO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.CERRADO
        caso.motivo_cierre = motivo_cierre
        caso.fecha_cierre = timezone.now().date()
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, f"Cerrado: {motivo_cierre}")
        return caso
    
    @classmethod
    @transaction.atomic
    def suspender_caso(cls, caso, usuario, motivo_suspension):
        """Cualquier estado operativo → SUSPENDIDO"""
        if not motivo_suspension:
            raise ValidationError("El motivo de suspensión es obligatorio")
        
        cls.validar_transicion(caso, EstadoCaso.SUSPENDIDO)
        
        estado_anterior = caso.estado
        caso.estado = EstadoCaso.SUSPENDIDO
        caso.motivo_suspension = motivo_suspension
        caso.save()
        
        cls.registrar_historial(caso, estado_anterior, caso.estado, usuario, f"Suspendido: {motivo_suspension}")
        return caso
    
    @classmethod
    @transaction.atomic
    def reactivar_caso(cls, caso, usuario, estado_destino, motivo_reactivacion):
        """SUSPENDIDO → estado anterior"""
        if caso.estado != EstadoCaso.SUSPENDIDO:
            raise ValidationError("Solo se pueden reactivar casos suspendidos")
        
        if not motivo_reactivacion:
            raise ValidationError("El motivo de reactivación es obligatorio")
        
        cls.validar_transicion(caso, estado_destino)
        
        estado_anterior = caso.estado
        caso.estado = estado_destino
        caso.motivo_suspension = ""  # Limpiar motivo de suspensión
        caso.save()
        
        cls.registrar_historial(
            caso, estado_anterior, caso.estado, usuario,
            f"Reactivado: {motivo_reactivacion}"
        )
        return caso


class ServicioDeteccionDuplicados:
    """Servicio para detectar casos duplicados"""
    
    @classmethod
    def detectar_duplicados(cls, ciudadano):
        """Detecta si el ciudadano ya tiene casos activos"""
        casos_activos = CasoNachec.objects.filter(
            ciudadano_titular=ciudadano
        ).exclude(
            estado__in=[EstadoCaso.CERRADO, EstadoCaso.RECHAZADO]
        )
        
        return casos_activos.exists(), casos_activos
    
    @classmethod
    def marcar_duplicado(cls, caso):
        """Marca un caso como duplicado"""
        caso.tiene_duplicado = True
        caso.save()


class ServicioSLA:
    """Servicio para calcular y validar SLAs"""
    
    @classmethod
    def calcular_sla_revision(cls, fecha_derivacion, dias_habiles=2):
        """Calcula SLA de revisión (48hs hábiles)"""
        fecha = fecha_derivacion
        dias_agregados = 0
        
        while dias_agregados < dias_habiles:
            fecha += timedelta(days=1)
            # Saltar fines de semana (5=sábado, 6=domingo)
            if fecha.weekday() < 5:
                dias_agregados += 1
        
        return fecha
    
    @classmethod
    def calcular_sla_relevamiento(cls, fecha_asignacion, dias_habiles=7):
        """Calcula SLA de relevamiento (7 días hábiles)"""
        return cls.calcular_sla_revision(fecha_asignacion, dias_habiles)
    
    @classmethod
    def esta_vencido(cls, fecha_sla):
        """Verifica si un SLA está vencido"""
        if not fecha_sla:
            return False
        return timezone.now().date() > fecha_sla
