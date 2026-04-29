from django.contrib import admin

from .models import (
    CampoDinamicoOpcion,
    CampoDinamicoTramite,
    EstadoTramite,
    EstadoTramiteTransicion,
    PrioridadTramite,
    RequisitoTramite,
    TipoTramite,
    Tramite,
    TramiteAdjunto,
    TramiteAsignacion,
    TramiteComentario,
    TramiteDatoDinamico,
    TramiteHistorial,
)


@admin.register(TipoTramite)
class TipoTramiteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "area", "municipio", "prioridad_default", "sla_horas", "activo")
    list_filter = (
        "activo",
        "area",
        "municipio",
        "requiere_pago",
        "requiere_turno",
        "permite_online",
        "permite_presencial",
        "requiere_adjunto",
        "requiere_validacion_manual",
    )
    search_fields = ("nombre", "codigo", "descripcion")
    raw_id_fields = ("area", "prioridad_default")
    ordering = ("orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EstadoTramite)
class EstadoTramiteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "municipio", "es_inicial", "es_final", "orden", "activo")
    list_filter = ("activo", "municipio", "es_inicial", "es_final")
    search_fields = ("nombre", "codigo", "descripcion")
    ordering = ("orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EstadoTramiteTransicion)
class EstadoTramiteTransicionAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "estado_origen",
        "estado_destino",
        "requiere_comentario",
        "requiere_asignado",
        "requiere_area_responsable",
        "activo",
    )
    list_filter = ("activo", "estado_origen", "estado_destino")
    search_fields = ("nombre", "descripcion", "estado_origen__nombre", "estado_destino__nombre")
    filter_horizontal = ("grupos_permitidos", "areas_permitidas")
    raw_id_fields = ("estado_origen", "estado_destino")
    ordering = ("estado_origen", "orden", "id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(PrioridadTramite)
class PrioridadTramiteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "nivel", "municipio", "activo")
    list_filter = ("activo", "municipio")
    search_fields = ("nombre", "codigo", "descripcion")
    ordering = ("nivel", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(RequisitoTramite)
class RequisitoTramiteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "tipo_tramite", "campo_dinamico", "obligatorio", "requiere_adjunto", "orden", "activo")
    list_filter = ("activo", "obligatorio", "requiere_adjunto", "tipo_tramite")
    search_fields = ("nombre", "codigo", "descripcion", "tipo_tramite__nombre", "campo_dinamico__nombre")
    raw_id_fields = ("tipo_tramite", "campo_dinamico")
    ordering = ("tipo_tramite", "orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CampoDinamicoTramite)
class CampoDinamicoTramiteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "tipo_tramite", "tipo_dato", "obligatorio", "orden", "activo")
    list_filter = ("activo", "tipo_tramite", "tipo_dato", "obligatorio")
    search_fields = ("nombre", "codigo", "descripcion", "tipo_tramite__nombre")
    raw_id_fields = ("tipo_tramite",)
    ordering = ("tipo_tramite", "orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CampoDinamicoOpcion)
class CampoDinamicoOpcionAdmin(admin.ModelAdmin):
    list_display = ("etiqueta", "valor", "campo", "orden", "activo")
    list_filter = ("activo", "campo", "campo__tipo_tramite")
    search_fields = ("etiqueta", "valor", "campo__nombre")
    raw_id_fields = ("campo",)
    ordering = ("campo", "orden", "etiqueta")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display = ("numero", "titulo", "estado", "prioridad", "area_actual", "asignado_a", "fecha_inicio", "activo")
    list_filter = ("activo", "estado", "prioridad", "tipo_tramite", "origen", "municipio", "visible_ciudadano")
    search_fields = ("numero", "titulo", "descripcion", "externo_id", "dni_contacto", "email_contacto")
    raw_id_fields = (
        "tipo_tramite",
        "estado",
        "prioridad",
        "area_actual",
        "area_responsable",
        "ciudadano",
        "provincia",
        "municipio",
        "localidad",
        "asignado_a",
        "creado_por",
        "actualizado_por",
    )
    readonly_fields = ("numero", "created_at", "updated_at")
    date_hierarchy = "fecha_inicio"
    ordering = ("-fecha_inicio", "-id")


@admin.register(TramiteHistorial)
class TramiteHistorialAdmin(admin.ModelAdmin):
    list_display = ("tramite", "accion", "usuario", "estado_anterior", "estado_nuevo", "fecha")
    list_filter = ("accion", "visible_ciudadano", "fecha")
    search_fields = ("tramite__numero", "accion", "comentario")
    raw_id_fields = (
        "tramite",
        "usuario",
        "estado_anterior",
        "estado_nuevo",
        "area_anterior",
        "area_nueva",
        "asignado_anterior",
        "asignado_nuevo",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-fecha", "-id")


@admin.register(TramiteAdjunto)
class TramiteAdjuntoAdmin(admin.ModelAdmin):
    list_display = ("tramite", "nombre_original", "tipo_mime", "tamano", "subido_por", "visible_ciudadano", "created_at")
    list_filter = ("visible_ciudadano", "created_at")
    search_fields = ("tramite__numero", "nombre_original", "tipo_mime")
    raw_id_fields = ("tramite", "subido_por")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TramiteComentario)
class TramiteComentarioAdmin(admin.ModelAdmin):
    list_display = ("tramite", "usuario", "ciudadano", "es_interno", "visible_ciudadano", "created_at")
    list_filter = ("es_interno", "visible_ciudadano", "created_at")
    search_fields = ("tramite__numero", "comentario", "usuario__username", "ciudadano__dni")
    raw_id_fields = ("tramite", "usuario", "ciudadano")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TramiteAsignacion)
class TramiteAsignacionAdmin(admin.ModelAdmin):
    list_display = ("tramite", "area", "usuario", "activa", "fecha_asignacion", "fecha_fin")
    list_filter = ("activa", "area", "fecha_asignacion")
    search_fields = ("tramite__numero", "area__nombre", "usuario__username", "motivo")
    raw_id_fields = ("tramite", "area", "usuario", "asignado_por")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-fecha_asignacion", "-id")


@admin.register(TramiteDatoDinamico)
class TramiteDatoDinamicoAdmin(admin.ModelAdmin):
    list_display = ("tramite", "campo", "activo", "updated_at")
    list_filter = ("activo", "campo", "campo__tipo_tramite")
    search_fields = ("tramite__numero", "campo__nombre", "campo__codigo")
    raw_id_fields = ("tramite", "campo")
    readonly_fields = ("created_at", "updated_at")
