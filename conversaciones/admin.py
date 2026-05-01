from django.contrib import admin
from .models import Conversacion, FlujoPortalConversacion, Mensaje


@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'dni_ciudadano', 'estado', 'fecha_inicio', 'operador_asignado']
    list_filter = ['tipo', 'estado', 'fecha_inicio']
    search_fields = ['dni_ciudadano', 'id']
    readonly_fields = ['fecha_inicio']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('operador_asignado', 'ciudadano_usuario').prefetch_related('mensajes')


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'remitente', 'contenido_corto', 'fecha_envio', 'leido']
    list_filter = ['remitente', 'fecha_envio', 'leido']
    search_fields = ['contenido']
    readonly_fields = ['fecha_envio']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('conversacion__operador_asignado')
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + "..." if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(FlujoPortalConversacion)
class FlujoPortalConversacionAdmin(admin.ModelAdmin):
    list_display = ['conversacion', 'canal', 'modulo', 'paso', 'derivado_operador', 'finalizado', 'updated_at']
    list_filter = ['canal', 'modulo', 'paso', 'derivado_operador', 'finalizado']
    search_fields = ['conversacion__id']
    readonly_fields = ['created_at', 'updated_at']
