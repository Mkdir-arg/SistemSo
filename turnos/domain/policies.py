STATUS_PENDING = "PENDIENTE"
STATUS_CONFIRMED = "CONFIRMADO"
STATUS_CANCELLED_BY_CITIZEN = "CANCELADO_CIU"
STATUS_CANCELLED_BY_SYSTEM = "CANCELADO_SIS"
STATUS_COMPLETED = "COMPLETADO"


def resolve_initial_state(*, requiere_aprobacion):
    return STATUS_PENDING if requiere_aprobacion else STATUS_CONFIRMED


def ensure_pending(status):
    if status != STATUS_PENDING:
        raise ValueError("Este turno ya fue procesado por otro operador.")


def ensure_cancellable(status):
    if status not in {STATUS_PENDING, STATUS_CONFIRMED}:
        raise ValueError("Este turno no puede cancelarse.")


def ensure_completable(status):
    if status != STATUS_CONFIRMED:
        raise ValueError("Solo pueden completarse turnos confirmados.")
