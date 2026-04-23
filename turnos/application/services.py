from django.db import transaction
from django.utils import timezone

from ..domain import (
    STATUS_CANCELLED_BY_CITIZEN,
    STATUS_CANCELLED_BY_SYSTEM,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    ensure_cancellable,
    ensure_completable,
    ensure_pending,
    resolve_initial_state,
)
from ..infrastructure import notifications, repositories


class TurnoActionError(Exception):
    pass


class TurnoNoDisponibleError(Exception):
    pass


class TurnosCiudadanoApplicationService:
    @staticmethod
    @transaction.atomic
    def reservar_turno_ciudadano(*, ciudadano, recurso, fecha, hora_inicio, hora_fin, motivo):
        ocupados = repositories.count_occupied_slots(
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
        )
        disponibilidad = repositories.get_matching_disponibilidad(
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        if not disponibilidad or ocupados >= disponibilidad.cupo_maximo:
            raise TurnoNoDisponibleError(
                "Este turno ya no esta disponible. Por favor elegi otro horario."
            )

        return repositories.create_turno_ciudadano(
            ciudadano=ciudadano,
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado=resolve_initial_state(
                requiere_aprobacion=recurso.requiere_aprobacion
            ),
            motivo_consulta=motivo,
        )

    @staticmethod
    def cancelar_turno_ciudadano(turno):
        try:
            ensure_cancellable(turno.estado)
        except ValueError:
            return False

        turno.estado = STATUS_CANCELLED_BY_CITIZEN
        repositories.save_turno(turno, update_fields=["estado", "modificado"])
        return True


class TurnosBackofficeApplicationService:
    @staticmethod
    def actualizar_notas(turno, notas):
        turno.notas_backoffice = notas.strip()
        repositories.save_turno(turno, update_fields=["notas_backoffice", "modificado"])
        return turno

    @staticmethod
    @transaction.atomic
    def aprobar_turno(turno_id, user, notas=""):
        turno = repositories.get_turno_for_update(turno_id)
        try:
            ensure_pending(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        if notas:
            turno.notas_backoffice = notas
        turno.estado = STATUS_CONFIRMED
        turno.aprobado_por = user
        turno.fecha_aprobacion = timezone.now()
        repositories.save_turno(turno)
        transaction.on_commit(lambda: notifications.send_confirmation(turno))
        return turno

    @staticmethod
    @transaction.atomic
    def rechazar_turno(turno_id, user, motivo):
        turno = repositories.get_turno_for_update(turno_id)
        try:
            ensure_pending(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        turno.estado = STATUS_CANCELLED_BY_SYSTEM
        turno.notas_backoffice = motivo
        turno.aprobado_por = user
        turno.fecha_aprobacion = timezone.now()
        repositories.save_turno(turno)
        transaction.on_commit(lambda: notifications.send_cancellation(turno, motivo=motivo))
        return turno

    @staticmethod
    def cancelar_turno(turno, motivo):
        try:
            ensure_cancellable(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        turno.estado = STATUS_CANCELLED_BY_SYSTEM
        turno.notas_backoffice = motivo
        repositories.save_turno(
            turno,
            update_fields=["estado", "notas_backoffice", "modificado"],
        )
        notifications.send_cancellation(turno, motivo=motivo)
        return turno

    @staticmethod
    def completar_turno(turno):
        try:
            ensure_completable(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        turno.estado = STATUS_COMPLETED
        repositories.save_turno(turno, update_fields=["estado", "modificado"])
        return turno
