from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import EventoCritico, SeguimientoContacto, LegajoAtencion
from .services import AlertasService
from conversaciones.models import Mensaje, Conversacion


@receiver(post_save, sender=EventoCritico)
def alerta_evento_critico(sender, instance, created, **kwargs):
    """Genera alerta automática cuando se crea un evento crítico"""
    if created:
        AlertasService.generar_alerta_evento_critico(
            instance.legajo, 
            instance.get_tipo_display(), 
            instance.detalle
        )


@receiver(post_save, sender=SeguimientoContacto)
def verificar_seguimiento_vencido(sender, instance, created, **kwargs):
    """Verifica si hay seguimientos vencidos al crear uno nuevo"""
    if created:
        # Generar alerta si es necesario basado en otros criterios
        pass


@receiver(post_save, sender=Mensaje)
def alerta_mensaje_ciudadano(sender, instance, created, **kwargs):
    """Genera alerta cuando ciudadano envía mensaje"""
    if created and instance.remitente == 'ciudadano':
        AlertasService.generar_alerta_mensaje_ciudadano(instance.conversacion)


@receiver(post_save, sender=LegajoAtencion)
def verificar_alertas_legajo(sender, instance, created, **kwargs):
    """Genera alertas automáticas al crear o modificar legajo"""
    if created:
        # Generar alertas iniciales
        AlertasService.generar_alertas_ciudadano(instance.ciudadano.id)
    else:
        # Verificar cambios críticos
        if hasattr(instance, '_state') and instance._state.adding is False:
            # Legajo modificado - regenerar alertas
            AlertasService.generar_alertas_ciudadano(instance.ciudadano.id)


@receiver(pre_save, sender=LegajoAtencion)
def detectar_cambio_riesgo(sender, instance, **kwargs):
    """Detecta cambios en el nivel de riesgo"""
    if instance.pk:
        try:
            legajo_anterior = LegajoAtencion.objects.get(pk=instance.pk)
            if legajo_anterior.nivel_riesgo != instance.nivel_riesgo:
                if instance.nivel_riesgo == 'ALTO':
                    # Crear alerta inmediata por cambio a riesgo alto
                    AlertasService.generar_alerta_evento_critico(
                        instance,
                        'CAMBIO_RIESGO',
                        f'Nivel de riesgo cambiado de {legajo_anterior.nivel_riesgo} a {instance.nivel_riesgo}'
                    )
        except LegajoAtencion.DoesNotExist:
            pass
