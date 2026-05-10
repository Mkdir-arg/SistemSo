from django.contrib import admin
from .models import ConfiguracionTurnos, DisponibilidadConfiguracion, SedeTurno


class DisponibilidadInline(admin.TabularInline):
    model = DisponibilidadConfiguracion
    extra = 0
    fields = ['dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno_min', 'cupo_maximo', 'activo']


@admin.register(ConfiguracionTurnos)
class ConfiguracionTurnosAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sede', 'tipo_tramite', 'modo_turno', 'requiere_aprobacion', 'activo', 'creado']
    list_filter = ['activo', 'requiere_aprobacion', 'modo_turno', 'sede']
    search_fields = ['nombre']
    inlines = [DisponibilidadInline]


@admin.register(DisponibilidadConfiguracion)
class DisponibilidadConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['configuracion', 'dia_semana', 'hora_inicio', 'hora_fin', 'duracion_turno_min', 'cupo_maximo', 'activo']
    list_filter = ['dia_semana', 'activo']


@admin.register(SedeTurno)
class SedeTurnoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'telefono', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'direccion', 'telefono']
    filter_horizontal = ['tramites_habilitados']
