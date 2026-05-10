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
from ..infrastructure import notifications, orm_repositories, unit_of_work


class TurnoActionError(Exception):
    pass


class TurnoNoDisponibleError(Exception):
    pass


class TurnosCiudadanoApplicationService:
    @staticmethod
    @unit_of_work.atomic
    def reservar_turno_ciudadano(*, ciudadano, recurso, fecha, hora_inicio, hora_fin, motivo):
        ocupados = orm_repositories.count_occupied_slots(
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
        )
        disponibilidad = orm_repositories.get_matching_disponibilidad(
            recurso=recurso,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )
        if not disponibilidad or ocupados >= disponibilidad.cupo_maximo:
            raise TurnoNoDisponibleError(
                "Este turno ya no esta disponible. Por favor elegi otro horario."
            )

        return orm_repositories.create_turno_ciudadano(
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
        orm_repositories.save_turno(turno, update_fields=["estado", "modificado"])
        return True


class TurnosBackofficeApplicationService:
    @staticmethod
    def _append_nota(turno, texto):
        texto = (texto or "").strip()
        if not texto:
            return turno.notas_backoffice or ""
        previo = (turno.notas_backoffice or "").strip()
        return f"{previo}\n{texto}".strip() if previo else texto

    @staticmethod
    def actualizar_notas(turno, notas):
        turno.notas_backoffice = notas.strip()
        orm_repositories.save_turno(turno, update_fields=["notas_backoffice", "modificado"])
        return turno

    @staticmethod
    @unit_of_work.atomic
    def aprobar_turno(turno_id, user, notas=""):
        turno = orm_repositories.get_turno_for_update(turno_id)
        try:
            ensure_pending(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        if notas:
            turno.notas_backoffice = notas
        turno.estado = STATUS_CONFIRMED
        turno.aprobado_por = user
        turno.fecha_aprobacion = unit_of_work.now()
        orm_repositories.save_turno(turno)
        unit_of_work.on_commit(lambda: notifications.send_confirmation(turno))
        return turno

    @staticmethod
    @unit_of_work.atomic
    def rechazar_turno(turno_id, user, motivo):
        turno = orm_repositories.get_turno_for_update(turno_id)
        try:
            ensure_pending(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        turno.estado = STATUS_CANCELLED_BY_SYSTEM
        turno.notas_backoffice = TurnosBackofficeApplicationService._append_nota(
            turno, f"[RECHAZO_SISTEMA] {motivo}"
        )
        turno.aprobado_por = user
        turno.fecha_aprobacion = unit_of_work.now()
        orm_repositories.save_turno(turno)
        unit_of_work.on_commit(lambda: notifications.send_cancellation(turno, motivo=motivo))
        return turno

    @staticmethod
    def cancelar_turno(turno, motivo, user=None):
        try:
            ensure_cancellable(turno.estado)
        except ValueError as exc:
            raise TurnoActionError(str(exc)) from exc

        turno.estado = STATUS_CANCELLED_BY_SYSTEM
        turno.notas_backoffice = TurnosBackofficeApplicationService._append_nota(
            turno, f"[CANCELACION_SISTEMA] {motivo}"
        )
        if user is not None:
            turno.aprobado_por = user
            turno.fecha_aprobacion = unit_of_work.now()
        orm_repositories.save_turno(
            turno,
            update_fields=["estado", "notas_backoffice", "aprobado_por", "fecha_aprobacion", "modificado"],
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
        orm_repositories.save_turno(turno, update_fields=["estado", "modificado"])
        return turno
