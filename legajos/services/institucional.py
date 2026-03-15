from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from ..models_institucional import (
    CasoInstitucional,
    DerivacionInstitucional,
    EstadoCaso,
    EstadoDerivacion,
    EstadoGlobal,
    EstadoPrograma,
)


class DerivacionService:
    """Servicio para gestión de derivaciones institucionales."""

    @staticmethod
    @transaction.atomic
    def aceptar_derivacion(derivacion_id, usuario, responsable_caso=None):
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        if hasattr(derivacion.institucion, "legajo_institucional"):
            estado_global = derivacion.institucion.legajo_institucional.estado_global
            if estado_global == EstadoGlobal.CERRADO:
                raise ValidationError(
                    "La institución está cerrada globalmente y no puede aceptar derivaciones"
                )

        if derivacion.institucion_programa.estado_programa != EstadoPrograma.ACTIVO:
            raise ValidationError(
                f"El programa está en estado "
                f"{derivacion.institucion_programa.get_estado_programa_display()} "
                "y no puede aceptar derivaciones"
            )

        if not derivacion.institucion_programa.activo:
            raise ValidationError("El programa no está activo en esta institución")

        if derivacion.institucion_programa.controlar_cupo:
            casos_activos = CasoInstitucional.objects.filter(
                institucion_programa=derivacion.institucion_programa,
                estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
            ).count()

            cupo_maximo = derivacion.institucion_programa.cupo_maximo

            if (
                casos_activos >= cupo_maximo
                and not derivacion.institucion_programa.permite_sobrecupo
            ):
                raise ValidationError(
                    f"Cupo lleno ({casos_activos}/{cupo_maximo}). "
                    "No se permite sobrecupo en este programa."
                )

        caso_existente = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
        ).first()

        if caso_existente:
            derivacion.estado = EstadoDerivacion.ACEPTADA_UNIFICADA
            derivacion.caso_creado = caso_existente
            derivacion.respondido_por = usuario
            derivacion.fecha_respuesta = timezone.now()
            derivacion.respuesta = f"Unificada con caso existente {caso_existente.codigo}"
            derivacion.save()
            return caso_existente, False

        ultima_version = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
        ).aggregate(Max("version"))["version__max"] or 0

        caso = CasoInstitucional.objects.create(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            version=ultima_version + 1,
            estado=EstadoCaso.ACTIVO,
            responsable_caso=responsable_caso or usuario,
            derivacion_origen=derivacion,
        )

        derivacion.estado = EstadoDerivacion.ACEPTADA
        derivacion.caso_creado = caso
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.respuesta = f"Caso creado: {caso.codigo}"
        derivacion.save()

        return caso, True

    @staticmethod
    @transaction.atomic
    def rechazar_derivacion(derivacion_id, usuario, motivo_rechazo):
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        derivacion.estado = EstadoDerivacion.RECHAZADA
        derivacion.respuesta = motivo_rechazo
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.save()


class CasoService:
    """Servicio para gestión de casos institucionales."""

    @staticmethod
    @transaction.atomic
    def cambiar_estado_caso(caso_id, nuevo_estado, usuario, observacion="", motivo_cierre=""):
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)

        estado_anterior = caso.estado
        if estado_anterior == nuevo_estado:
            raise ValidationError("El caso ya está en ese estado")

        caso.estado = nuevo_estado

        if nuevo_estado in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            caso.fecha_cierre = timezone.now().date()
            if motivo_cierre:
                caso.motivo_cierre = motivo_cierre

        if observacion:
            caso.notas = f"{caso.notas}\n\n{observacion}" if caso.notas else observacion

        caso.save()
        return caso

    @staticmethod
    @transaction.atomic
    def reabrir_caso(caso_id, usuario, observacion=""):
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)

        if caso.estado not in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            raise ValidationError("Solo se pueden reabrir casos cerrados o egresados")

        caso.estado = EstadoCaso.ACTIVO
        caso.fecha_cierre = None

        if observacion:
            nota_reapertura = f"[REAPERTURA] {observacion}"
            caso.notas = f"{caso.notas}\n\n{nota_reapertura}" if caso.notas else nota_reapertura

        caso.save()
        return caso
