from django.conf import settings
from django.contrib.auth.models import Group
from django.db import IntegrityError, models
from django.utils import timezone


class AuditModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True


class Area(AuditModel):
    nombre = models.CharField(max_length=120, db_index=True)
    descripcion = models.TextField(blank=True)
    codigo = models.CharField(max_length=40, db_index=True)
    email_contacto = models.EmailField(blank=True)
    telefono_contacto = models.CharField(max_length=40, blank=True)
    orden = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="areas_reclamos",
    )

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ["orden", "nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "municipio"], name="reclamos_area_codigo_municipio_uk"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})" if self.codigo else self.nombre


class PrioridadReclamo(AuditModel):
    nombre = models.CharField(max_length=120, db_index=True)
    codigo = models.CharField(max_length=40, db_index=True)
    descripcion = models.TextField(blank=True)
    nivel = models.PositiveSmallIntegerField(db_index=True)
    color = models.CharField(max_length=20, blank=True)
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prioridades_reclamo",
    )

    class Meta:
        verbose_name = "Prioridad de reclamo"
        verbose_name_plural = "Prioridades de reclamo"
        ordering = ["nivel", "nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "municipio"], name="reclamos_prioridad_codigo_municipio_uk"),
        ]

    def __str__(self):
        return f"{self.nombre} (N{self.nivel})"


class EstadoReclamo(AuditModel):
    nombre = models.CharField(max_length=120, db_index=True)
    codigo = models.CharField(max_length=40, db_index=True)
    descripcion = models.TextField(blank=True)
    es_inicial = models.BooleanField(default=False, db_index=True)
    es_final = models.BooleanField(default=False, db_index=True)
    color = models.CharField(max_length=20, blank=True)
    orden = models.PositiveIntegerField(default=0, db_index=True)
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="estados_reclamo",
    )

    class Meta:
        verbose_name = "Estado de reclamo"
        verbose_name_plural = "Estados de reclamo"
        ordering = ["orden", "nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["codigo", "municipio"], name="reclamos_estado_codigo_municipio_uk"),
        ]

    def __str__(self):
        return self.nombre


class EstadoReclamoTransicion(AuditModel):
    estado_origen = models.ForeignKey(
        "reclamos.EstadoReclamo",
        on_delete=models.CASCADE,
        related_name="transiciones_salida",
    )
    estado_destino = models.ForeignKey(
        "reclamos.EstadoReclamo",
        on_delete=models.CASCADE,
        related_name="transiciones_entrada",
    )
    nombre = models.CharField(max_length=120, db_index=True)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0, db_index=True)
    requiere_comentario = models.BooleanField(default=False)
    requiere_asignado = models.BooleanField(default=False)
    requiere_area_responsable = models.BooleanField(default=False)
    grupos_permitidos = models.ManyToManyField(
        Group,
        blank=True,
        related_name="transiciones_estado_reclamo",
    )
    areas_permitidas = models.ManyToManyField(
        "reclamos.Area",
        blank=True,
        related_name="transiciones_estado_reclamo",
    )

    class Meta:
        verbose_name = "Transicion de estado de reclamo"
        verbose_name_plural = "Transiciones de estado de reclamo"
        ordering = ["estado_origen", "orden", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["estado_origen", "estado_destino"],
                name="reclamos_estado_transicion_origen_destino_uk",
            ),
        ]
        indexes = [
            models.Index(fields=["estado_origen", "activo"]),
            models.Index(fields=["estado_destino", "activo"]),
        ]

    def __str__(self):
        return f"{self.estado_origen.nombre} -> {self.estado_destino.nombre}"


class TipoReclamo(AuditModel):
    nombre = models.CharField(max_length=120, db_index=True)
    descripcion = models.TextField(blank=True)
    area = models.ForeignKey("reclamos.Area", on_delete=models.PROTECT, related_name="tipos_reclamo")
    requiere_ubicacion = models.BooleanField(default=False)
    requiere_adjunto = models.BooleanField(default=False)
    permite_anonimo = models.BooleanField(default=False)
    sla_horas = models.PositiveIntegerField(null=True, blank=True)
    prioridad_default = models.ForeignKey(
        "reclamos.PrioridadReclamo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tipos_reclamo_default",
    )
    orden = models.PositiveIntegerField(default=0, db_index=True)
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tipos_reclamo",
    )

    class Meta:
        verbose_name = "Tipo de reclamo"
        verbose_name_plural = "Tipos de reclamo"
        ordering = ["orden", "nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["nombre", "municipio"], name="reclamos_tipo_nombre_municipio_uk"),
        ]

    def __str__(self):
        return self.nombre


class CampoDinamicoReclamo(AuditModel):
    class TipoDato(models.TextChoices):
        TEXTO = "texto", "Texto"
        NUMERO = "numero", "Numero"
        FECHA = "fecha", "Fecha"
        BOOLEANO = "booleano", "Booleano"
        SELECCION = "seleccion", "Seleccion"
        EMAIL = "email", "Email"
        TELEFONO = "telefono", "Telefono"
        DNI = "dni", "DNI"
        ARCHIVO = "archivo", "Archivo"

    tipo_reclamo = models.ForeignKey(
        "reclamos.TipoReclamo",
        on_delete=models.CASCADE,
        related_name="campos_dinamicos",
    )
    nombre = models.CharField(max_length=120, db_index=True)
    codigo = models.CharField(max_length=60, db_index=True)
    descripcion = models.TextField(blank=True)
    tipo_dato = models.CharField(max_length=20, choices=TipoDato.choices, default=TipoDato.TEXTO)
    obligatorio = models.BooleanField(default=False, db_index=True)
    orden = models.PositiveIntegerField(default=0, db_index=True)
    placeholder = models.CharField(max_length=120, blank=True)
    ayuda = models.CharField(max_length=255, blank=True)
    valor_default = models.CharField(max_length=255, blank=True)
    longitud_maxima = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Campo dinamico de reclamo"
        verbose_name_plural = "Campos dinamicos de reclamo"
        ordering = ["tipo_reclamo", "orden", "nombre", "id"]
        constraints = [
            models.UniqueConstraint(fields=["tipo_reclamo", "codigo"], name="reclamos_campo_tipo_codigo_uk"),
        ]

    def __str__(self):
        return f"{self.tipo_reclamo.nombre} - {self.nombre}"


class CampoDinamicoOpcion(AuditModel):
    campo = models.ForeignKey(
        "reclamos.CampoDinamicoReclamo",
        on_delete=models.CASCADE,
        related_name="opciones",
    )
    valor = models.CharField(max_length=120)
    etiqueta = models.CharField(max_length=120)
    orden = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        verbose_name = "Opcion de campo dinamico"
        verbose_name_plural = "Opciones de campo dinamico"
        ordering = ["campo", "orden", "etiqueta", "id"]
        constraints = [
            models.UniqueConstraint(fields=["campo", "valor"], name="reclamos_campo_opcion_valor_uk"),
        ]

    def __str__(self):
        return f"{self.campo.nombre} - {self.etiqueta}"


class Reclamo(AuditModel):
    class Origen(models.TextChoices):
        WEB = "web", "Web"
        APP = "app", "App"
        CHAT = "chat", "Chat"
        WHATSAPP = "whatsapp", "WhatsApp"
        OPERADOR = "operador", "Operador"
        TELEFONO = "telefono", "Telefono"

    numero = models.CharField(max_length=40, unique=True, db_index=True, blank=True)
    titulo = models.CharField(max_length=200, db_index=True)
    descripcion = models.TextField()
    detalle_interno = models.TextField(blank=True)

    tipo_reclamo = models.ForeignKey("reclamos.TipoReclamo", on_delete=models.PROTECT, related_name="reclamos")
    estado = models.ForeignKey("reclamos.EstadoReclamo", on_delete=models.PROTECT, related_name="reclamos")
    prioridad = models.ForeignKey("reclamos.PrioridadReclamo", on_delete=models.PROTECT, related_name="reclamos")
    area_actual = models.ForeignKey("reclamos.Area", on_delete=models.PROTECT, related_name="reclamos_area_actual")
    area_responsable = models.ForeignKey(
        "reclamos.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_area_responsable",
    )

    ciudadano = models.ForeignKey(
        "legajos.Ciudadano",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos",
    )

    nombre_contacto = models.CharField(max_length=120, blank=True)
    apellido_contacto = models.CharField(max_length=120, blank=True)
    dni_contacto = models.CharField(max_length=20, blank=True)
    email_contacto = models.EmailField(blank=True)
    telefono_contacto = models.CharField(max_length=40, blank=True)

    provincia = models.ForeignKey(
        "core.Provincia",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos",
    )
    municipio = models.ForeignKey(
        "core.Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos",
    )
    localidad = models.ForeignKey(
        "core.Localidad",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos",
    )
    barrio = models.CharField(max_length=120, blank=True)
    calle = models.CharField(max_length=120, blank=True)
    numero_calle = models.CharField(max_length=20, blank=True)
    piso = models.CharField(max_length=20, blank=True)
    departamento = models.CharField(max_length=20, blank=True)
    entre_calles = models.CharField(max_length=255, blank=True)
    referencia = models.TextField(blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    origen = models.CharField(max_length=20, choices=Origen.choices, default=Origen.WEB, db_index=True)
    canal_detalle = models.CharField(max_length=120, blank=True)
    externo_id = models.CharField(max_length=120, blank=True, db_index=True)

    fecha_ingreso = models.DateTimeField(default=timezone.now, db_index=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, db_index=True)
    fecha_primera_respuesta = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_asignados",
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_creados",
    )
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_actualizados",
    )

    sla_horas = models.PositiveIntegerField(null=True, blank=True)
    es_anonimo = models.BooleanField(default=False)
    requiere_inspeccion = models.BooleanField(default=False)
    visible_ciudadano = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Reclamo"
        verbose_name_plural = "Reclamos"
        ordering = ["-fecha_ingreso", "-id"]
        indexes = [
            models.Index(fields=["numero"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["prioridad"]),
            models.Index(fields=["area_actual"]),
            models.Index(fields=["tipo_reclamo"]),
            models.Index(fields=["fecha_ingreso"]),
        ]

    def __str__(self):
        return f"{self.numero} - {self.titulo}"

    @classmethod
    def generar_numero(cls):
        prefijo = f"REC-{timezone.localdate():%Y%m%d}"
        ultimo = (
            cls.objects.filter(numero__startswith=prefijo)
            .order_by("-numero")
            .values_list("numero", flat=True)
            .first()
        )
        secuencia = 1
        if ultimo and "-" in ultimo:
            try:
                secuencia = int(ultimo.rsplit("-", 1)[1]) + 1
            except ValueError:
                secuencia = 1
        return f"{prefijo}-{secuencia:06d}"

    def save(self, *args, **kwargs):
        if self.numero:
            return super().save(*args, **kwargs)

        for _ in range(5):
            self.numero = self.generar_numero()
            try:
                return super().save(*args, **kwargs)
            except IntegrityError:
                self.numero = ""
                continue
        raise IntegrityError("No se pudo generar un numero unico para el reclamo.")


class ReclamoHistorial(AuditModel):
    reclamo = models.ForeignKey("reclamos.Reclamo", on_delete=models.CASCADE, related_name="historial")
    fecha = models.DateTimeField(default=timezone.now, db_index=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_historial",
    )
    accion = models.CharField(max_length=120)
    estado_anterior = models.ForeignKey(
        "reclamos.EstadoReclamo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_estado_anterior",
    )
    estado_nuevo = models.ForeignKey(
        "reclamos.EstadoReclamo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_estado_nuevo",
    )
    area_anterior = models.ForeignKey(
        "reclamos.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_area_anterior",
    )
    area_nueva = models.ForeignKey(
        "reclamos.Area",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_area_nueva",
    )
    asignado_anterior = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_historial_asignado_anterior",
    )
    asignado_nuevo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_historial_asignado_nuevo",
    )
    comentario = models.TextField(blank=True)
    visible_ciudadano = models.BooleanField(default=False)
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Historial de reclamo"
        verbose_name_plural = "Historial de reclamos"
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["reclamo", "fecha"])]

    def __str__(self):
        return f"{self.reclamo.numero} - {self.accion} - {self.fecha:%Y-%m-%d %H:%M}"


class ReclamoAdjunto(AuditModel):
    reclamo = models.ForeignKey("reclamos.Reclamo", on_delete=models.CASCADE, related_name="adjuntos")
    archivo = models.FileField(upload_to="reclamos/adjuntos/%Y/%m/")
    nombre_original = models.CharField(max_length=255)
    tipo_mime = models.CharField(max_length=120, blank=True)
    tamano = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_adjuntos_subidos",
    )
    visible_ciudadano = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Adjunto de reclamo"
        verbose_name_plural = "Adjuntos de reclamo"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.reclamo.numero} - {self.nombre_original}"

    def save(self, *args, **kwargs):
        if self.archivo and not self.nombre_original:
            self.nombre_original = self.archivo.name.split("/")[-1]
        if self.archivo and not self.tamano:
            try:
                self.tamano = self.archivo.size
            except Exception:
                pass
        return super().save(*args, **kwargs)


class ReclamoComentario(AuditModel):
    reclamo = models.ForeignKey("reclamos.Reclamo", on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_comentarios_usuario",
    )
    ciudadano = models.ForeignKey(
        "legajos.Ciudadano",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_comentarios",
    )
    comentario = models.TextField()
    es_interno = models.BooleanField(default=False)
    visible_ciudadano = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Comentario de reclamo"
        verbose_name_plural = "Comentarios de reclamo"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.reclamo.numero} - comentario {self.id}"


class ReclamoAsignacion(AuditModel):
    reclamo = models.ForeignKey("reclamos.Reclamo", on_delete=models.CASCADE, related_name="asignaciones")
    area = models.ForeignKey("reclamos.Area", on_delete=models.PROTECT, related_name="asignaciones_reclamo")
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_asignaciones",
    )
    fecha_asignacion = models.DateTimeField(default=timezone.now, db_index=True)
    fecha_fin = models.DateTimeField(null=True, blank=True, db_index=True)
    motivo = models.TextField(blank=True)
    asignado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reclamos_asignaciones_realizadas",
    )
    activa = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = "Asignacion de reclamo"
        verbose_name_plural = "Asignaciones de reclamo"
        ordering = ["-fecha_asignacion", "-id"]
        indexes = [models.Index(fields=["reclamo", "activa"])]

    def __str__(self):
        destino = self.usuario.get_username() if self.usuario else self.area.nombre
        return f"{self.reclamo.numero} -> {destino}"


class ReclamoDatoDinamico(AuditModel):
    reclamo = models.ForeignKey("reclamos.Reclamo", on_delete=models.CASCADE, related_name="datos_dinamicos")
    campo = models.ForeignKey("reclamos.CampoDinamicoReclamo", on_delete=models.CASCADE, related_name="datos_cargados")
    valor = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Dato dinamico de reclamo"
        verbose_name_plural = "Datos dinamicos de reclamo"
        ordering = ["reclamo", "campo__orden", "id"]
        constraints = [
            models.UniqueConstraint(fields=["reclamo", "campo"], name="reclamos_dato_reclamo_campo_uk"),
        ]
        indexes = [models.Index(fields=["reclamo", "campo"])]

    def __str__(self):
        return f"{self.reclamo.numero} - {self.campo.nombre}"
