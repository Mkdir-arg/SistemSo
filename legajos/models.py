from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from core.models import TimeStamped, LegajoBase, Institucion
# from simple_history.models import HistoricalRecords  # Comentado temporalmente

# Alias para compatibilidad
DispositivoRed = Institucion


class Ciudadano(TimeStamped):
    """Modelo para ciudadanos del sistema de legajos"""
    
    class Genero(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"
        NO_BINARIO = "X", "No binario"
    
    dni = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=120, db_index=True)
    apellido = models.CharField(max_length=120, db_index=True)
    fecha_nacimiento = models.DateField(null=True, blank=True, db_index=True)
    genero = models.CharField(max_length=1, choices=Genero.choices, blank=True, db_index=True)
    telefono = models.CharField(max_length=40, blank=True, db_index=True)
    email = models.EmailField(blank=True, db_index=True)
    domicilio = models.CharField(max_length=240, blank=True)
    activo = models.BooleanField(default=True, db_index=True)
    
    # Historial de cambios
    # history = HistoricalRecords()  # Comentado temporalmente
    
    class Meta:
        verbose_name = "Ciudadano"
        verbose_name_plural = "Ciudadanos"
        indexes = [
            models.Index(fields=["dni"]),
            models.Index(fields=["apellido", "nombre"]),
            models.Index(fields=["activo", "apellido"]),
            models.Index(fields=["email"]),
        ]
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"
    
    # Managers
    objects = models.Manager()  # Manager por defecto
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del ciudadano"""
        return f"{self.nombre} {self.apellido}"


class Profesional(TimeStamped):
    """Profesionales que trabajan con legajos"""
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    matricula = models.CharField(max_length=60, blank=True)
    rol = models.CharField(max_length=80, blank=True)
    
    class Meta:
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"


class LegajoAtencion(LegajoBase):
    """Legajo de atención individual para ciudadanos"""
    
    class ViaIngreso(models.TextChoices):
        ESPONTANEA = "ESPONTANEA", "Consulta espontánea"
        DERIVACION = "DERIVACION", "Derivación"
        JUDICIAL = "JUDICIAL", "Judicial"
        HOSPITAL = "HOSPITAL", "Hospital/Guardia"
    
    class NivelRiesgo(models.TextChoices):
        BAJO = "BAJO", "Bajo"
        MEDIO = "MEDIO", "Medio"
        ALTO = "ALTO", "Alto"
    
    ciudadano = models.ForeignKey(
        Ciudadano, 
        on_delete=models.PROTECT, 
        related_name="legajos"
    )
    dispositivo = models.ForeignKey(
        Institucion, 
        on_delete=models.PROTECT, 
        related_name="legajos",
        verbose_name="Institución",
        null=True,
        blank=True
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legajos_atencion_responsable",
        limit_choices_to={'groups__name': 'Responsable'},
        verbose_name="Responsable",
        help_text="Usuario con rol de Responsable asignado al legajo"
    )
    via_ingreso = models.CharField(
        max_length=20, 
        choices=ViaIngreso.choices, 
        default=ViaIngreso.ESPONTANEA,
        db_index=True
    )
    fecha_admision = models.DateField(auto_now_add=True, db_index=True)
    plan_vigente = models.BooleanField(default=False, db_index=True)
    nivel_riesgo = models.CharField(
        max_length=20, 
        choices=NivelRiesgo.choices, 
        default=NivelRiesgo.BAJO,
        db_index=True
    )
    
    # Historial de cambios
    # history = HistoricalRecords()  # Comentado temporalmente
    
    class Meta:
        verbose_name = "Acompañamiento"
        verbose_name_plural = "Acompañamientos"
        indexes = [
            models.Index(fields=["ciudadano", "dispositivo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["nivel_riesgo", "fecha_admision"]),
            models.Index(fields=["plan_vigente", "estado"]),
            models.Index(fields=["via_ingreso", "fecha_admision"]),
            models.Index(fields=["dispositivo", "estado"]),
        ]
    
    def __str__(self):
        return f"Legajo {self.codigo} - {self.ciudadano}"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('legajos:detalle', kwargs={'pk': self.pk})
    
    def puede_cerrar(self):
        """Verifica si el legajo puede cerrarse"""
        from datetime import datetime, timedelta
        if self.estado == 'CERRADO':
            return False, "El legajo ya está cerrado"
        
        # Verificar seguimiento reciente (últimos 30 días)
        fecha_limite = datetime.now().date() - timedelta(days=30)
        tiene_seguimiento_reciente = self.seguimientos.filter(
            creado__date__gte=fecha_limite
        ).exists()
        
        if self.plan_vigente and not tiene_seguimiento_reciente:
            return False, "Requiere seguimiento reciente o justificación para cerrar"
        
        return True, "Puede cerrarse"
    
    def cerrar(self, motivo_cierre=None, usuario=None):
        """Cierra el legajo"""
        from datetime import datetime
        puede, mensaje = self.puede_cerrar()
        if not puede and not motivo_cierre:
            raise ValidationError(mensaje)
        
        self.estado = 'CERRADO'
        self.fecha_cierre = datetime.now().date()
        if motivo_cierre:
            if not self.notas:
                self.notas = f"Motivo de cierre: {motivo_cierre}"
            else:
                self.notas += f"\n\nMotivo de cierre: {motivo_cierre}"
        self.save()
    
    def reabrir(self, motivo_reapertura=None, usuario=None):
        """Reabre el legajo"""
        if self.estado != 'CERRADO':
            raise ValidationError("Solo se pueden reabrir legajos cerrados")
        
        self.estado = 'EN_SEGUIMIENTO'
        self.fecha_cierre = None
        if motivo_reapertura:
            if not self.notas:
                self.notas = f"Motivo de reapertura: {motivo_reapertura}"
            else:
                self.notas += f"\n\nMotivo de reapertura: {motivo_reapertura}"
        self.save()
    
    @property
    def dias_desde_admision(self):
        """Días transcurridos desde la admisión"""
        from datetime import datetime
        return (datetime.now().date() - self.fecha_admision).days
    
    # Managers
    objects = models.Manager()  # Manager por defecto
    
    @property
    def tiempo_primer_contacto(self):
        """Días hasta el primer seguimiento"""
        primer_seguimiento = self.seguimientos.order_by('creado').first()
        if primer_seguimiento:
            return (primer_seguimiento.creado.date() - self.fecha_admision).days
        return None


class Consentimiento(TimeStamped):
    """Consentimientos informados para tratamiento de datos"""
    
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.PROTECT)
    texto = models.TextField()
    firmado_por = models.CharField(max_length=160)
    fecha_firma = models.DateField()
    archivo = models.FileField(upload_to="consentimientos/", null=True, blank=True)
    vigente = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Consentimiento"
        verbose_name_plural = "Consentimientos"
    
    def __str__(self):
        return f"Consentimiento {self.ciudadano} - {self.fecha_firma}"


class EvaluacionInicial(TimeStamped):
    """Evaluación inicial clínico-psicosocial del legajo"""
    
    legajo = models.OneToOneField(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="evaluacion"
    )
    situacion_consumo = models.TextField(
        blank=True,
        verbose_name="Situación de Consumo",
        help_text="Descripción de la situación actual de consumo"
    )
    antecedentes = models.TextField(
        blank=True,
        verbose_name="Antecedentes",
        help_text="Antecedentes médicos, psiquiátricos y de consumo"
    )
    red_apoyo = models.TextField(
        blank=True,
        verbose_name="Red de Apoyo",
        help_text="Descripción de la red de apoyo familiar y social"
    )
    condicion_social = models.TextField(
        blank=True,
        verbose_name="Condición Social",
        help_text="Situación socioeconómica, vivienda, trabajo, educación"
    )
    tamizajes = models.JSONField(
        blank=True, 
        null=True,
        verbose_name="Tamizajes",
        help_text="Resultados de tamizajes aplicados (ej: ASSIST, PHQ-9)"
    )
    riesgo_suicida = models.BooleanField(
        default=False,
        verbose_name="Riesgo Suicida",
        help_text="Indica si presenta riesgo suicida",
        db_index=True
    )
    violencia = models.BooleanField(
        default=False,
        verbose_name="Situación de Violencia",
        help_text="Indica si presenta situación de violencia",
        db_index=True
    )
    
    class Meta:
        verbose_name = "Evaluación Inicial"
        verbose_name_plural = "Evaluaciones Iniciales"
        indexes = [
            models.Index(fields=["riesgo_suicida"]),
            models.Index(fields=["violencia"]),
        ]
    
    def __str__(self):
        return f"Evaluación - {self.legajo.codigo}"
    
    @property
    def tiene_riesgos(self):
        """Indica si tiene algún tipo de riesgo identificado"""
        return self.riesgo_suicida or self.violencia
    
    @property
    def riesgos_identificados(self):
        """Lista de riesgos identificados"""
        riesgos = []
        if self.riesgo_suicida:
            riesgos.append("Riesgo Suicida")
        if self.violencia:
            riesgos.append("Violencia")
        return riesgos
    
    @property
    def tiene_eventos_criticos(self):
        """Indica si el legajo tiene eventos críticos recientes"""
        from datetime import datetime, timedelta
        fecha_limite = datetime.now().date() - timedelta(days=30)
        return self.legajo.eventos.filter(creado__date__gte=fecha_limite).exists()


class Objetivo(models.Model):
    """Objetivos del plan de intervención"""
    
    legajo = models.ForeignKey(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="objetivos"
    )
    descripcion = models.CharField(max_length=240)
    indicador_exito = models.CharField(max_length=240, blank=True)
    cumplido = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Objetivo"
        verbose_name_plural = "Objetivos"
    
    def __str__(self):
        return f"Objetivo - {self.descripcion[:50]}"


class PlanIntervencion(TimeStamped):
    """Plan de intervención para el legajo"""
    
    legajo = models.ForeignKey(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="planes"
    )
    profesional = models.ForeignKey(
        Profesional, 
        on_delete=models.PROTECT
    )
    vigente = models.BooleanField(default=True, db_index=True)
    actividades = models.JSONField(
        blank=True, 
        null=True,
        help_text="Lista de actividades: [{\"accion\":\"Entrevista\",\"freq\":\"semanal\",\"responsable\":\"operador\"}]"
    )
    
    class Meta:
        verbose_name = "Plan de Intervención"
        verbose_name_plural = "Planes de Intervención"
        indexes = [
            models.Index(fields=["legajo", "vigente"]),
            models.Index(fields=["profesional", "vigente"]),
        ]
    
    def __str__(self):
        return f"Plan {self.legajo.codigo} - {'Vigente' if self.vigente else 'Histórico'}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Solo validar si el legajo ya está asignado
        if self.vigente and hasattr(self, 'legajo') and self.legajo and PlanIntervencion.objects.filter(
            legajo=self.legajo, vigente=True
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Ya existe un plan vigente para este legajo.")
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        self.clean()
        with transaction.atomic():
            if self.vigente:
                PlanIntervencion.objects.select_for_update().filter(
                    legajo=self.legajo, vigente=True
                ).exclude(pk=self.pk).update(vigente=False)
                LegajoAtencion.objects.filter(pk=self.legajo_id).update(plan_vigente=True)
            super().save(*args, **kwargs)


class SeguimientoContacto(TimeStamped):
    """Contactos y seguimientos del legajo"""
    
    class TipoContacto(models.TextChoices):
        ENTREVISTA = "ENTREVISTA", "Entrevista"
        VISITA = "VISITA", "Visita"
        LLAMADA = "LLAMADA", "Llamada"
        TALLER = "TALLER", "Taller"
    
    class Adherencia(models.TextChoices):
        ADECUADA = "ADECUADA", "Adecuada"
        PARCIAL = "PARCIAL", "Parcial"
        NULA = "NULA", "Nula"
    
    legajo = models.ForeignKey(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="seguimientos"
    )
    profesional = models.ForeignKey(
        Profesional, 
        on_delete=models.PROTECT
    )
    tipo = models.CharField(
        max_length=40, 
        choices=TipoContacto.choices,
        db_index=True
    )
    descripcion = models.TextField()
    adherencia = models.CharField(
        max_length=20, 
        choices=Adherencia.choices,
        blank=True,
        db_index=True
    )
    adjuntos = models.FileField(
        upload_to="seguimientos/", 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = "Seguimiento"
        verbose_name_plural = "Seguimientos"
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["legajo", "-creado"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["adherencia", "legajo"]),
            models.Index(fields=["profesional", "-creado"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.legajo.codigo} ({self.creado.date()})"


class Derivacion(TimeStamped):
    """Derivaciones entre dispositivos"""
    
    class Urgencia(models.TextChoices):
        BAJA = "BAJA", "Baja"
        MEDIA = "MEDIA", "Media"
        ALTA = "ALTA", "Alta"
    
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        ACEPTADA = "ACEPTADA", "Aceptada"
        RECHAZADA = "RECHAZADA", "Rechazada"
    
    legajo = models.ForeignKey(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="derivaciones"
    )
    destino = models.ForeignKey(
        Institucion, 
        on_delete=models.PROTECT, 
        related_name="derivaciones_destino",
        verbose_name="Institución Destino"
    )
    actividad_destino = models.ForeignKey(
        'PlanFortalecimiento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="derivaciones",
        verbose_name="Actividad Específica"
    )
    motivo = models.TextField()
    urgencia = models.CharField(
        max_length=20, 
        choices=Urgencia.choices, 
        default=Urgencia.MEDIA,
        db_index=True
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True
    )
    respuesta = models.CharField(max_length=120, blank=True)
    fecha_aceptacion = models.DateField(null=True, blank=True, db_index=True)
    
    class Meta:
        verbose_name = "Derivación"
        verbose_name_plural = "Derivaciones"
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["legajo", "estado"]),
            models.Index(fields=["urgencia"]),
            models.Index(fields=["estado", "urgencia"]),
            models.Index(fields=["destino", "estado"]),
        ]
    
    def __str__(self):
        return f"Derivación a {self.destino.nombre}"
    
    def clean(self):
        if hasattr(self, 'destino') and self.destino and not self.destino.activo:
            raise ValidationError("No es posible derivar a un dispositivo inactivo.")


class EventoCritico(TimeStamped):
    """Eventos críticos del legajo"""
    
    class TipoEvento(models.TextChoices):
        SOBREDOSIS = "SOBREDOSIS", "Sobredosis"
        CRISIS = "CRISIS", "Crisis aguda"
        VIOLENCIA = "VIOLENCIA", "Violencia"
        INTERNACION = "INTERNACION", "Internación"
    
    legajo = models.ForeignKey(
        LegajoAtencion, 
        on_delete=models.CASCADE, 
        related_name="eventos"
    )
    tipo = models.CharField(
        max_length=40, 
        choices=TipoEvento.choices,
        db_index=True
    )
    detalle = models.TextField()
    notificado_a = models.JSONField(
        blank=True, 
        null=True,
        help_text="Lista de familiares/autoridades notificadas"
    )
    
    class Meta:
        verbose_name = "Evento Crítico"
        verbose_name_plural = "Eventos Críticos"
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["legajo", "tipo"]),
            models.Index(fields=["-creado"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.legajo.codigo} ({self.creado.date()})"


class Adjunto(TimeStamped):
    """Adjuntos genéricos para cualquier modelo"""
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")
    archivo = models.FileField(upload_to="adjuntos/")
    etiqueta = models.CharField(max_length=120, blank=True)
    
    class Meta:
        verbose_name = "Adjunto"
        verbose_name_plural = "Adjuntos"
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
    
    def __str__(self):
        return f"Adjunto - {self.etiqueta or self.archivo.name}"


class AlertaEventoCritico(TimeStamped):
    """Registro de alertas vistas por responsables"""
    
    evento = models.ForeignKey(
        EventoCritico,
        on_delete=models.CASCADE,
        related_name="alertas_vistas"
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alertas_eventos_vistas"
    )
    fecha_cierre = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Alerta Evento Crítico"
        verbose_name_plural = "Alertas Eventos Críticos"
        unique_together = ["evento", "responsable"]
        indexes = [
            models.Index(fields=["responsable", "fecha_cierre"]),
        ]
    
    def __str__(self):
        return f"Alerta {self.evento.tipo} vista por {self.responsable.username}"


class AlertaCiudadano(TimeStamped):
    """Sistema de alertas automáticas para ciudadanos"""
    
    class TipoAlerta(models.TextChoices):
        RIESGO_ALTO = "RIESGO_ALTO", "Riesgo Alto"
        RIESGO_SUICIDA = "RIESGO_SUICIDA", "Riesgo Suicida"
        VIOLENCIA = "VIOLENCIA", "Situación de Violencia"
        SIN_CONTACTO = "SIN_CONTACTO", "Sin Contacto Prolongado"
        SIN_EVALUACION = "SIN_EVALUACION", "Sin Evaluación Inicial"
        SIN_PLAN = "SIN_PLAN", "Sin Plan de Intervención"
        EVENTO_CRITICO = "EVENTO_CRITICO", "Evento Crítico Reciente"
        DERIVACION_PENDIENTE = "DERIVACION_PENDIENTE", "Derivación Pendiente"
        SIN_RED_FAMILIAR = "SIN_RED_FAMILIAR", "Sin Red Familiar"
        SIN_CONSENTIMIENTO = "SIN_CONSENTIMIENTO", "Sin Consentimiento"
        CONTACTOS_FALLIDOS = "CONTACTOS_FALLIDOS", "Contactos Fallidos"
        PLAN_VENCIDO = "PLAN_VENCIDO", "Plan Vencido"
    
    class Prioridad(models.TextChoices):
        CRITICA = "CRITICA", "Crítica"
        ALTA = "ALTA", "Alta"
        MEDIA = "MEDIA", "Media"
        BAJA = "BAJA", "Baja"
    
    ciudadano = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name="alertas"
    )
    legajo = models.ForeignKey(
        LegajoAtencion,
        on_delete=models.CASCADE,
        related_name="alertas",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=30, choices=TipoAlerta.choices, db_index=True)
    prioridad = models.CharField(max_length=10, choices=Prioridad.choices, db_index=True)
    mensaje = models.CharField(max_length=200)
    activa = models.BooleanField(default=True, db_index=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True, db_index=True)
    cerrada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_cerradas"
    )
    
    class Meta:
        verbose_name = "Alerta de Ciudadano"
        verbose_name_plural = "Alertas de Ciudadanos"
        ordering = ["-creado"]
        indexes = [
            models.Index(fields=["ciudadano", "activa"]),
            models.Index(fields=["tipo", "prioridad"]),
            models.Index(fields=["legajo", "activa"]),
            models.Index(fields=["activa", "prioridad", "-creado"]),
            models.Index(fields=["cerrada_por", "fecha_cierre"]),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.ciudadano}"
    
    def cerrar(self, usuario=None):
        """Cerrar la alerta"""
        self.activa = False
        self.fecha_cierre = timezone.now()
        self.cerrada_por = usuario
        self.save()
    
    @property
    def color_css(self):
        """Retorna las clases CSS según la prioridad"""
        colores = {
            'CRITICA': 'bg-red-100 text-red-800 border-red-200',
            'ALTA': 'bg-orange-100 text-orange-800 border-orange-200',
            'MEDIA': 'bg-yellow-100 text-yellow-800 border-yellow-200',
            'BAJA': 'bg-blue-100 text-blue-800 border-blue-200',
        }
        return colores.get(self.prioridad, 'bg-gray-100 text-gray-800 border-gray-200')


class LegajoInstitucional(TimeStamped):
    """Legajo institucional para gestión de instituciones"""
    
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        OBSERVACION = "OBSERVACION", "En Observación"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"
        CERRADO = "CERRADO", "Cerrado"
    
    institucion = models.OneToOneField(
        Institucion,
        on_delete=models.CASCADE,
        related_name="legajo_institucional"
    )
    codigo = models.CharField(max_length=50, unique=True, editable=False)
    
    # Estado global - controla operatividad de TODOS los programas
    estado_global = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        db_index=True,
        verbose_name="Estado Global",
        help_text="Si es CERRADO, bloquea todos los programas de la institución"
    )
    
    responsable_sedronar = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legajos_institucionales_responsable"
    )
    fecha_apertura = models.DateField(auto_now_add=True)
    fecha_cierre = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Legajo Institucional"
        verbose_name_plural = "Legajos Institucionales"
    
    def __str__(self):
        return f"Legajo {self.codigo} - {self.institucion.nombre}"
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            from datetime import datetime
            self.codigo = f"INST-{datetime.now().strftime('%Y%m%d')}-{self.institucion.id:04d}"
        super().save(*args, **kwargs)


class PersonalInstitucion(TimeStamped):
    """Personal de la institución"""
    
    class TipoPersonal(models.TextChoices):
        DIRECTOR = "DIRECTOR", "Director/a"
        COORDINADOR = "COORDINADOR", "Coordinador/a"
        PROFESIONAL = "PROFESIONAL", "Profesional"
        OPERADOR = "OPERADOR", "Operador/a"
        ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo/a"
        OTRO = "OTRO", "Otro"
    
    legajo_institucional = models.ForeignKey(
        LegajoInstitucional,
        on_delete=models.CASCADE,
        related_name="personal"
    )
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="personal_institucion"
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TipoPersonal.choices)
    titulo_profesional = models.CharField(max_length=200, blank=True)
    matricula = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)
    
    def crear_usuario(self):
        """Crea un usuario del sistema para este personal"""
        if not self.usuario:
            from django.contrib.auth.models import Group
            
            username = f"{self.nombre.lower()}.{self.apellido.lower()}"
            # Si ya existe, agregar DNI
            if User.objects.filter(username=username).exists():
                username = f"{username}.{self.dni}"
            
            usuario = User.objects.create_user(
                username=username,
                email=f"{username}@{self.legajo_institucional.institucion.nombre.lower().replace(' ', '')}.com",
                first_name=self.nombre,
                last_name=self.apellido,
                password=self.dni  # Password temporal = DNI
            )
            
            # Asignar grupo según tipo
            grupo_map = {
                'DIRECTOR': 'Directores',
                'COORDINADOR': 'Coordinadores', 
                'PROFESIONAL': 'Profesionales',
                'OPERADOR': 'Operadores',
                'ADMINISTRATIVO': 'Administrativos'
            }
            
            grupo_nombre = grupo_map.get(self.tipo, 'Staff')
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            usuario.groups.add(grupo)
            
            self.usuario = usuario
            self.save()
            
            return usuario
        return self.usuario
    
    class Meta:
        verbose_name = "Personal de Institución"
        verbose_name_plural = "Personal de Instituciones"
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} - {self.get_tipo_display()}"


class CapacitacionPersonal(TimeStamped):
    """Capacitaciones del personal"""
    
    personal = models.ForeignKey(
        PersonalInstitucion,
        on_delete=models.CASCADE,
        related_name="capacitaciones"
    )
    nombre_capacitacion = models.CharField(max_length=200)
    institucion_capacitadora = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horas_catedra = models.PositiveIntegerField(null=True, blank=True)
    certificado = models.FileField(upload_to="capacitaciones/", blank=True)
    
    class Meta:
        verbose_name = "Capacitación de Personal"
        verbose_name_plural = "Capacitaciones de Personal"
    
    def __str__(self):
        return f"{self.nombre_capacitacion} - {self.personal}"


class EvaluacionInstitucional(TimeStamped):
    """Evaluación de capacidades institucionales"""
    
    legajo_institucional = models.ForeignKey(
        LegajoInstitucional,
        on_delete=models.CASCADE,
        related_name="evaluaciones"
    )
    fecha_evaluacion = models.DateField()
    evaluador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Capacidades institucionales
    infraestructura = models.PositiveIntegerField(
        help_text="Puntuación 1-10",
        choices=[(i, i) for i in range(1, 11)]
    )
    recursos_humanos = models.PositiveIntegerField(
        help_text="Puntuación 1-10",
        choices=[(i, i) for i in range(1, 11)]
    )
    programas_servicios = models.PositiveIntegerField(
        help_text="Puntuación 1-10",
        choices=[(i, i) for i in range(1, 11)]
    )
    gestion_administrativa = models.PositiveIntegerField(
        help_text="Puntuación 1-10",
        choices=[(i, i) for i in range(1, 11)]
    )
    
    observaciones = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Evaluación Institucional"
        verbose_name_plural = "Evaluaciones Institucionales"
    
    def __str__(self):
        return f"Evaluación {self.fecha_evaluacion} - {self.legajo_institucional.institucion.nombre}"
    
    @property
    def puntaje_total(self):
        return (self.infraestructura + self.recursos_humanos + 
                self.programas_servicios + self.gestion_administrativa) / 4


class PlanFortalecimiento(TimeStamped):
    """Actividades y programas institucionales"""
    
    class TipoActividad(models.TextChoices):
        PREVENCION = "PREVENCION", "Prevención"
        TRATAMIENTO = "TRATAMIENTO", "Tratamiento"
        REDUCCION_RIESGO = "REDUCCION_RIESGO", "Reducción de Riesgo"
        REINSERCION = "REINSERCION", "Reinserción Social"
        CAPACITACION = "CAPACITACION", "Capacitación"
        OTRO = "OTRO", "Otro"
    
    class SubtipoActividad(models.TextChoices):
        # Prevención
        ÑACHEC = "ÑACHEC", "ÑACHEC"
        PREVENCION_SELECTIVA = "PREVENCION_SELECTIVA", "Prevención Selectiva"
        PREVENCION_INDICADA = "PREVENCION_INDICADA", "Prevención Indicada"
        # Tratamiento
        AMBULATORIO = "AMBULATORIO", "Ambulatorio"
        INTERNACION = "INTERNACION", "Internación"
        HOSPITAL_DIA = "HOSPITAL_DIA", "Hospital de Día"
        # Reducción de Riesgo
        INTERCAMBIO_JERINGAS = "INTERCAMBIO_JERINGAS", "Intercambio de Jeringas"
        TESTEO_VIH = "TESTEO_VIH", "Testeo VIH"
        CONSEJERIA = "CONSEJERIA", "Consejería"
        # Reinserción
        LABORAL = "LABORAL", "Laboral"
        EDUCATIVA = "EDUCATIVA", "Educativa"
        SOCIAL = "SOCIAL", "Social"
        # Capacitación
        PROFESIONAL = "PROFESIONAL", "Profesional"
        OPERADORES = "OPERADORES", "Operadores"
        COMUNIDAD = "COMUNIDAD", "Comunidad"
    
    class Estado(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        SUSPENDIDO = "SUSPENDIDO", "Suspendido"
        FINALIZADO = "FINALIZADO", "Finalizado"
    
    legajo_institucional = models.ForeignKey(
        LegajoInstitucional,
        on_delete=models.CASCADE,
        related_name="planes_fortalecimiento"
    )
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TipoActividad.choices)
    subtipo = models.CharField(max_length=30, choices=SubtipoActividad.choices)
    descripcion = models.TextField(blank=True)
    cupo_ciudadanos = models.PositiveIntegerField(default=0, help_text="Capacidad máxima de ciudadanos")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=Estado.choices, default=Estado.ACTIVO)
    
    class Meta:
        verbose_name = "Actividad Institucional"
        verbose_name_plural = "Actividades Institucionales"
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()}"


class StaffActividad(TimeStamped):
    """Staff asignado a una actividad"""
    
    actividad = models.ForeignKey(
        PlanFortalecimiento,
        on_delete=models.CASCADE,
        related_name="staff"
    )
    personal = models.ForeignKey(
        PersonalInstitucion,
        on_delete=models.CASCADE
    )
    rol_en_actividad = models.CharField(
        max_length=100,
        help_text="Ej: Coordinador, Terapeuta, Operador"
    )
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Staff de Actividad"
        verbose_name_plural = "Staff de Actividades"
        unique_together = ['actividad', 'personal']
    
    def __str__(self):
        return f"{self.personal} - {self.actividad.nombre}"


class IndicadorInstitucional(TimeStamped):
    """Indicadores y métricas institucionales"""
    
    legajo_institucional = models.ForeignKey(
        LegajoInstitucional,
        on_delete=models.CASCADE,
        related_name="indicadores"
    )
    periodo = models.CharField(
        max_length=20,
        help_text="Ej: 2024-01, 2024-Q1"
    )
    beneficiarios_atendidos = models.PositiveIntegerField(default=0)
    derivaciones_recibidas = models.PositiveIntegerField(default=0)
    derivaciones_enviadas = models.PositiveIntegerField(default=0)
    servicios_brindados = models.JSONField(
        blank=True,
        null=True,
        help_text="Lista de servicios y cantidades"
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Indicador Institucional"
        verbose_name_plural = "Indicadores Institucionales"
        unique_together = ['legajo_institucional', 'periodo']
    
    def __str__(self):
        return f"Indicadores {self.periodo} - {self.legajo_institucional.institucion.nombre}"


# Importar modelos de contactos
from .models_contactos import (
    HistorialContacto, VinculoFamiliar, ProfesionalTratante,
    DispositivoVinculado, ContactoEmergencia
)

# Importar timezone
from django.utils import timezone


class HistorialActividad(TimeStamped):
    """Historial de cambios en actividades"""
    
    class TipoAccion(models.TextChoices):
        CREACION = "CREACION", "Creación"
        MODIFICACION = "MODIFICACION", "Modificación"
        SUSPENSION = "SUSPENSION", "Suspensión"
        FINALIZACION = "FINALIZACION", "Finalización"
        REACTIVACION = "REACTIVACION", "Reactivación"
    
    actividad = models.ForeignKey(
        PlanFortalecimiento,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    accion = models.CharField(max_length=20, choices=TipoAccion.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    datos_anteriores = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Historial de Actividad"
        verbose_name_plural = "Historiales de Actividades"
        ordering = ["-creado"]


class HistorialStaff(TimeStamped):
    """Historial de asignaciones de staff"""
    
    class TipoAccion(models.TextChoices):
        ASIGNACION = "ASIGNACION", "Asignación"
        DESASIGNACION = "DESASIGNACION", "Desasignación"
        CAMBIO_ROL = "CAMBIO_ROL", "Cambio de Rol"
    
    staff = models.ForeignKey(
        StaffActividad,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    accion = models.CharField(max_length=20, choices=TipoAccion.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name = "Historial de Staff"
        verbose_name_plural = "Historiales de Staff"
        ordering = ["-creado"]


class HistorialDerivacion(TimeStamped):
    """Historial de cambios en derivaciones"""
    
    class TipoAccion(models.TextChoices):
        CREACION = "CREACION", "Creación"
        ACEPTACION = "ACEPTACION", "Aceptación"
        RECHAZO = "RECHAZO", "Rechazo"
    
    derivacion = models.ForeignKey(
        Derivacion,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    accion = models.CharField(max_length=20, choices=TipoAccion.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    estado_anterior = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Historial de Derivación"
        verbose_name_plural = "Historiales de Derivaciones"
        ordering = ["-creado"]


class InscriptoActividad(TimeStamped):
    """Ciudadanos inscritos en actividades"""
    
    class Estado(models.TextChoices):
        INSCRITO = "INSCRITO", "Inscrito"
        ACTIVO = "ACTIVO", "Activo"
        FINALIZADO = "FINALIZADO", "Finalizado"
        ABANDONADO = "ABANDONADO", "Abandonado"
    
    actividad = models.ForeignKey(
        PlanFortalecimiento,
        on_delete=models.CASCADE,
        related_name="inscriptos"
    )
    ciudadano = models.ForeignKey(
        Ciudadano,
        on_delete=models.CASCADE,
        related_name="actividades_inscrito"
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.INSCRITO)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    fecha_finalizacion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Inscripto en Actividad"
        verbose_name_plural = "Inscriptos en Actividades"
        unique_together = ['actividad', 'ciudadano']
        ordering = ["-fecha_inscripcion"]


class HistorialInscripto(TimeStamped):
    """Historial de cambios en inscripciones"""
    
    class TipoAccion(models.TextChoices):
        INSCRIPCION = "INSCRIPCION", "Inscripción"
        ACTIVACION = "ACTIVACION", "Activación"
        FINALIZACION = "FINALIZACION", "Finalización"
        ABANDONO = "ABANDONO", "Abandono"
    
    inscripto = models.ForeignKey(
        InscriptoActividad,
        on_delete=models.CASCADE,
        related_name="historial"
    )
    accion = models.CharField(max_length=20, choices=TipoAccion.choices)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    estado_anterior = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Historial de Inscripto"
        verbose_name_plural = "Historiales de Inscriptos"
        ordering = ["-creado"]


class RegistroAsistencia(TimeStamped):
    """Registro de asistencia a actividades"""
    
    class Estado(models.TextChoices):
        PRESENTE = "PRESENTE", "Presente"
        AUSENTE = "AUSENTE", "Ausente"
        JUSTIFICADO = "JUSTIFICADO", "Ausente Justificado"
        TARDANZA = "TARDANZA", "Tardanza"
    
    inscripto = models.ForeignKey(
        InscriptoActividad,
        on_delete=models.CASCADE,
        related_name="asistencias"
    )
    fecha = models.DateField()
    estado = models.CharField(max_length=15, choices=Estado.choices)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="asistencias_registradas"
    )
    
    class Meta:
        verbose_name = "Registro de Asistencia"
        verbose_name_plural = "Registros de Asistencia"
        unique_together = ['inscripto', 'fecha']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.inscripto.ciudadano.nombre_completo} - {self.fecha} - {self.get_estado_display()}"
    
    def clean(self):
        """Validar que no exista otro registro para el mismo inscripto en la misma fecha"""
        if self.inscripto and self.fecha:
            existe = RegistroAsistencia.objects.filter(
                inscripto=self.inscripto,
                fecha=self.fecha
            ).exclude(pk=self.pk).exists()
            
            if existe:
                raise ValidationError(
                    f'Ya existe un registro de asistencia para {self.inscripto.ciudadano.nombre_completo} '
                    f'en la fecha {self.fecha.strftime("%d/%m/%Y")}'
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class AlertaAusentismo(TimeStamped):
    """Alertas por ausentismo prolongado"""
    
    class TipoAlerta(models.TextChoices):
        AUSENTISMO_3_DIAS = "AUSENTISMO_3", "3 días consecutivos"
        AUSENTISMO_5_DIAS = "AUSENTISMO_5", "5 días consecutivos"
        AUSENTISMO_SEMANAL = "AUSENTISMO_SEMANAL", "Más del 50% semanal"
    
    inscripto = models.ForeignKey(
        InscriptoActividad,
        on_delete=models.CASCADE,
        related_name="alertas_ausentismo"
    )
    tipo = models.CharField(max_length=20, choices=TipoAlerta.choices)
    dias_ausente = models.PositiveIntegerField()
    fecha_inicio_ausencia = models.DateField()
    activa = models.BooleanField(default=True)
    vista_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertas_ausentismo_vistas"
    )
    
    class Meta:
        verbose_name = "Alerta de Ausentismo"
        verbose_name_plural = "Alertas de Ausentismo"
        ordering = ['-creado']
    
    def __str__(self):
        return f"Alerta {self.get_tipo_display()} - {self.inscripto.ciudadano.nombre_completo}"