from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LegajoAtencion
from .models_programas import Programa, InscripcionPrograma


@receiver(post_save, sender=LegajoAtencion)
def crear_inscripcion_programa_sedronar(sender, instance, created, **kwargs):
    """
    Crea automáticamente una InscripcionPrograma cuando se crea un LegajoAtencion
    """
    if created:
        try:
            programa_sedronar = Programa.objects.get(tipo='ACOMPANAMIENTO_SEDRONAR')
            
            # Verificar que no exista ya
            existe = InscripcionPrograma.objects.filter(
                ciudadano=instance.ciudadano,
                programa=programa_sedronar
            ).exists()
            
            if not existe:
                InscripcionPrograma.objects.create(
                    ciudadano=instance.ciudadano,
                    programa=programa_sedronar,
                    via_ingreso='DIRECTO',
                    estado='ACTIVO',
                    responsable=instance.responsable,
                    legajo_id=instance.id,
                    fecha_inscripcion=instance.fecha_apertura,
                    fecha_inicio=instance.fecha_apertura,
                    notas=f'Creado automáticamente desde LegajoAtencion {instance.codigo}'
                )
        except Programa.DoesNotExist:
            pass  # Programa SEDRONAR no existe aún
