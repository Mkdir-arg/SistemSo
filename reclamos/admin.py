from django.contrib import admin

from .models import (
    Area,
    CampoDinamicoOpcion,
    CampoDinamicoReclamo,
    EstadoReclamo,
    EstadoReclamoTransicion,
    PrioridadReclamo,
    Reclamo,
    ReclamoAdjunto,
    ReclamoAsignacion,
    ReclamoComentario,
    ReclamoDatoDinamico,
    ReclamoHistorial,
    TipoReclamo,
)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "municipio", "activo", "orden", "updated_at")
    list_filter = ("activo", "municipio")
    search_fields = ("nombre", "codigo", "email_contacto")
    ordering = ("orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TipoReclamo)
class TipoReclamoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "area", "municipio", "prioridad_default", "sla_horas", "activo")
    list_filter = ("activo", "area", "municipio", "requiere_ubicacion", "requiere_adjunto", "permite_anonimo")
    search_fields = ("nombre", "descripcion")
    raw_id_fields = ("area", "prioridad_default")
    ordering = ("orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EstadoReclamo)
class EstadoReclamoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "municipio", "es_inicial", "es_final", "orden", "activo")
    list_filter = ("activo", "municipio", "es_inicial", "es_final")
    search_fields = ("nombre", "codigo", "descripcion")
    ordering = ("orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EstadoReclamoTransicion)
class EstadoReclamoTransicionAdmin(admin.ModelAdmin):
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


@admin.register(PrioridadReclamo)
class PrioridadReclamoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "nivel", "municipio", "activo")
    list_filter = ("activo", "municipio")
    search_fields = ("nombre", "codigo", "descripcion")
    ordering = ("nivel", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CampoDinamicoReclamo)
class CampoDinamicoReclamoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "tipo_reclamo", "tipo_dato", "obligatorio", "orden", "activo")
    list_filter = ("activo", "tipo_reclamo", "tipo_dato", "obligatorio")
    search_fields = ("nombre", "codigo", "descripcion", "tipo_reclamo__nombre")
    raw_id_fields = ("tipo_reclamo",)
    ordering = ("tipo_reclamo", "orden", "nombre")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CampoDinamicoOpcion)
class CampoDinamicoOpcionAdmin(admin.ModelAdmin):
    list_display = ("etiqueta", "valor", "campo", "orden", "activo")
    list_filter = ("activo", "campo", "campo__tipo_reclamo")
    search_fields = ("etiqueta", "valor", "campo__nombre")
    raw_id_fields = ("campo",)
    ordering = ("campo", "orden", "etiqueta")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Reclamo)
class ReclamoAdmin(admin.ModelAdmin):
    list_display = ("numero", "titulo", "estado", "prioridad", "area_actual", "asignado_a", "fecha_ingreso", "activo")
    list_filter = ("activo", "estado", "prioridad", "tipo_reclamo", "origen", "municipio", "visible_ciudadano")
    search_fields = ("numero", "titulo", "descripcion", "externo_id", "dni_contacto", "email_contacto")
    raw_id_fields = (
        "tipo_reclamo",
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
    date_hierarchy = "fecha_ingreso"
    ordering = ("-fecha_ingreso", "-id")


@admin.register(ReclamoHistorial)
class ReclamoHistorialAdmin(admin.ModelAdmin):
    list_display = ("reclamo", "accion", "usuario", "estado_anterior", "estado_nuevo", "fecha")
    list_filter = ("accion", "visible_ciudadano", "fecha")
    search_fields = ("reclamo__numero", "accion", "comentario")
    raw_id_fields = (
        "reclamo",
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


@admin.register(ReclamoAdjunto)
class ReclamoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ("reclamo", "nombre_original", "tipo_mime", "tamano", "subido_por", "visible_ciudadano", "created_at")
    list_filter = ("visible_ciudadano", "created_at")
    search_fields = ("reclamo__numero", "nombre_original", "tipo_mime")
    raw_id_fields = ("reclamo", "subido_por")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReclamoComentario)
class ReclamoComentarioAdmin(admin.ModelAdmin):
    list_display = ("reclamo", "usuario", "ciudadano", "es_interno", "visible_ciudadano", "created_at")
    list_filter = ("es_interno", "visible_ciudadano", "created_at")
    search_fields = ("reclamo__numero", "comentario", "usuario__username", "ciudadano__dni")
    raw_id_fields = ("reclamo", "usuario", "ciudadano")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReclamoAsignacion)
class ReclamoAsignacionAdmin(admin.ModelAdmin):
    list_display = ("reclamo", "area", "usuario", "activa", "fecha_asignacion", "fecha_fin")
    list_filter = ("activa", "area", "fecha_asignacion")
    search_fields = ("reclamo__numero", "area__nombre", "usuario__username", "motivo")
    raw_id_fields = ("reclamo", "area", "usuario", "asignado_por")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-fecha_asignacion", "-id")


@admin.register(ReclamoDatoDinamico)
class ReclamoDatoDinamicoAdmin(admin.ModelAdmin):
    list_display = ("reclamo", "campo", "activo", "updated_at")
    list_filter = ("activo", "campo", "campo__tipo_reclamo")
    search_fields = ("reclamo__numero", "campo__nombre", "campo__codigo")
    raw_id_fields = ("reclamo", "campo")
    readonly_fields = ("created_at", "updated_at")
