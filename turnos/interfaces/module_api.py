from ..application import (
    TurnoActionError,
    TurnoNoDisponibleError,
    TurnosBackofficeApplicationService,
    TurnosCiudadanoApplicationService,
)


def reservar_turno_ciudadano(**kwargs):
    return TurnosCiudadanoApplicationService.reservar_turno_ciudadano(**kwargs)


def cancelar_turno_ciudadano(turno):
    return TurnosCiudadanoApplicationService.cancelar_turno_ciudadano(turno)


def actualizar_notas_turno_backoffice(turno, notas):
    return TurnosBackofficeApplicationService.actualizar_notas(turno, notas)


def aprobar_turno_backoffice(turno_id, user, notas=""):
    return TurnosBackofficeApplicationService.aprobar_turno(turno_id, user, notas=notas)


def rechazar_turno_backoffice(turno_id, user, motivo):
    return TurnosBackofficeApplicationService.rechazar_turno(turno_id, user, motivo)


def cancelar_turno_backoffice(turno, motivo):
    return TurnosBackofficeApplicationService.cancelar_turno(turno, motivo)


def completar_turno_backoffice(turno):
    return TurnosBackofficeApplicationService.completar_turno(turno)
