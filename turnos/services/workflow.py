from ..interfaces.module_api import (
    TurnoActionError,
    actualizar_notas_turno_backoffice,
    aprobar_turno_backoffice,
    cancelar_turno_backoffice,
    completar_turno_backoffice,
    rechazar_turno_backoffice,
)


class TurnosBackofficeService:
    actualizar_notas = staticmethod(actualizar_notas_turno_backoffice)
    aprobar_turno = staticmethod(aprobar_turno_backoffice)
    rechazar_turno = staticmethod(rechazar_turno_backoffice)
    cancelar_turno = staticmethod(cancelar_turno_backoffice)
    completar_turno = staticmethod(completar_turno_backoffice)
