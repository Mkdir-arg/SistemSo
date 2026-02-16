from django.contrib import admin
from .models_programas import Programa, InscripcionPrograma, DerivacionPrograma


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'tipo', 'activo', 'orden')
    list_filter = ('activo', 'tipo')
    search_fields = ('codigo', 'nombre')
    ordering = ('orden', 'nombre')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'tipo', 'descripcion')
        }),
        ('Configuración Visual', {
            'fields': ('color', 'icono', 'orden')
        }),
        ('Configuración del Programa', {
            'fields': ('requiere_evaluacion', 'requiere_plan', 'requiere_seguimientos', 'modelo_legajo')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


@admin.register(InscripcionPrograma)
class InscripcionProgramaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'ciudadano', 'programa', 'estado', 'responsable', 'fecha_inscripcion')
    list_filter = ('estado', 'via_ingreso', 'programa', 'fecha_inscripcion')
    search_fields = ('codigo', 'ciudadano__dni', 'ciudadano__nombre', 'ciudadano__apellido')
    readonly_fields = ('codigo', 'creado', 'modificado')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('ciudadano', 'programa', 'responsable')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'ciudadano', 'programa')
        }),
        ('Estado', {
            'fields': ('estado', 'via_ingreso', 'responsable')
        }),
        ('Fechas', {
            'fields': ('fecha_inscripcion', 'fecha_inicio', 'fecha_cierre')
        }),
        ('Observaciones', {
            'fields': ('notas', 'motivo_cierre')
        }),
        ('Auditoría', {
            'fields': ('creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DerivacionPrograma)
class DerivacionProgramaAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'programa_origen', 'programa_destino', 'estado', 'urgencia', 'derivado_por', 'creado')
    list_filter = ('estado', 'urgencia', 'programa_destino', 'creado')
    search_fields = ('ciudadano__dni', 'ciudadano__nombre', 'ciudadano__apellido', 'motivo')
    readonly_fields = ('creado', 'modificado', 'fecha_respuesta')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'ciudadano', 'programa_origen', 'programa_destino', 
            'derivado_por', 'respondido_por', 'inscripcion_creada'
        )
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('ciudadano', 'programa_origen', 'programa_destino')
        }),
        ('Derivación', {
            'fields': ('motivo', 'urgencia', 'estado', 'derivado_por')
        }),
        ('Respuesta', {
            'fields': ('respuesta', 'fecha_respuesta', 'respondido_por', 'inscripcion_creada')
        }),
        ('Auditoría', {
            'fields': ('creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )
