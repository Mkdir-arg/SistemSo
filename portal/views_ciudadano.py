from .views_ciudadano_auth import (
    CiudadanoLoginView,
    CiudadanoLogoutView,
    CiudadanoPasswordResetCompleteView,
    CiudadanoPasswordResetConfirmView,
    CiudadanoPasswordResetDoneView,
    CiudadanoPasswordResetView,
    RegistroStep1View,
    RegistroStep2View,
)
from .views_ciudadano_consultas import (
    ciudadano_consulta_detalle,
    ciudadano_enviar_mensaje,
    ciudadano_mis_consultas,
    ciudadano_nueva_consulta,
)
from .views_ciudadano_perfil import (
    ciudadano_cambio_email,
    ciudadano_cambio_password,
    ciudadano_confirmar_email,
    ciudadano_mi_perfil,
    ciudadano_mis_datos,
    ciudadano_mis_programas,
    ciudadano_programa_detalle,
)
from .views_ciudadano_turnos import (
    ciudadano_cancelar_turno,
    ciudadano_confirmar_turno,
    ciudadano_mis_turnos,
    ciudadano_solicitar_turno,
    ciudadano_turno_calendario,
    ciudadano_turno_confirmado,
    ciudadano_turno_slots,
)
