from django.urls import path

from .views import (
    PortalCiudadanoHomeView,
    PortalCiudadanoChatView,
    PortalCiudadanoLoginView,
    PortalCiudadanoLogoutView,
    PortalCiudadanoMisSolicitudesView,
    PortalCiudadanoMiPerfilView,
    PortalCiudadanoReclamoConfirmarView,
    PortalCiudadanoReclamoDetalleView,
    PortalCiudadanoReclamoDetalleSolicitudView,
    PortalCiudadanoReclamoEnviadoView,
    PortalCiudadanoReclamosView,
    PortalCiudadanoTramiteConfirmarView,
    PortalCiudadanoTramiteDetalleSolicitudView,
    PortalCiudadanoTramiteDetalleView,
    PortalCiudadanoTramiteInicioView,
    PortalCiudadanoTramiteEnviadoView,
    PortalCiudadanoTramitesView,
    PortalCiudadanoRegistroStep1View,
    PortalCiudadanoRegistroStep2View,
    PortalCiudadanoPasswordResetView,
    PortalCiudadanoPasswordResetDoneView,
    PortalCiudadanoPasswordResetConfirmView,
    PortalCiudadanoPasswordResetCompleteView,
    portal_ciudadano_cancelar_turno,
    portal_ciudadano_confirmar_turno,
    portal_ciudadano_mis_programas,
    portal_ciudadano_mis_turnos,
    portal_ciudadano_programa_detalle,
    portal_ciudadano_solicitar_turno,
    portal_ciudadano_turno_calendario,
    portal_ciudadano_turno_confirmado,
    portal_ciudadano_turnos_disponibles_por_fecha,
    portal_ciudadano_agenda_sede,
    portal_ciudadano_agenda_general,
    portal_ciudadano_turno_slots,
    portal_ciudadano_mis_datos,
    portal_ciudadano_cambio_password,
    portal_ciudadano_cambio_email,
    portal_ciudadano_confirmar_email,
    portal_ciudadano_mis_consultas,
    portal_ciudadano_nueva_consulta,
    portal_ciudadano_consulta_detalle,
    portal_ciudadano_enviar_mensaje,
    portal_ciudadano_notificaciones_turnos_leidas,
)

app_name = "portal_ciudadano"

urlpatterns = [
    path("", PortalCiudadanoHomeView.as_view(), name="home"),
    path("chat/", PortalCiudadanoChatView.as_view(), name="chat"),
    path("login/", PortalCiudadanoLoginView.as_view(), name="login"),
    path("logout/", PortalCiudadanoLogoutView.as_view(), name="logout"),

    # Registro
    path("registro/", PortalCiudadanoRegistroStep1View.as_view(), name="registro_step1"),
    path("registro/verificar/", PortalCiudadanoRegistroStep2View.as_view(), name="registro_step2"),

    # Password reset
    path("password/reset/", PortalCiudadanoPasswordResetView.as_view(), name="password_reset"),
    path("password/reset/enviado/", PortalCiudadanoPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/", PortalCiudadanoPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/reset/completado/", PortalCiudadanoPasswordResetCompleteView.as_view(), name="password_reset_complete"),

    # Perfil
    path("mi-perfil/", PortalCiudadanoMiPerfilView.as_view(), name="mi_perfil"),
    path("mis-solicitudes/", PortalCiudadanoMisSolicitudesView.as_view(), name="mis_solicitudes"),
    path("programas/", portal_ciudadano_mis_programas, name="programas"),
    path("programas/<int:pk>/", portal_ciudadano_programa_detalle, name="programa_detalle"),

    # Mis datos
    path("mis-datos/", portal_ciudadano_mis_datos, name="mis_datos"),
    path("mis-datos/cambio-password/", portal_ciudadano_cambio_password, name="cambio_password"),
    path("mis-datos/cambio-email/", portal_ciudadano_cambio_email, name="cambio_email"),
    path("mis-datos/confirmar-email/<uuid:token>/", portal_ciudadano_confirmar_email, name="confirmar_email"),

    # Consultas
    path("consultas/", portal_ciudadano_mis_consultas, name="mis_consultas"),
    path("consultas/nueva/", portal_ciudadano_nueva_consulta, name="nueva_consulta"),
    path("consultas/<int:pk>/", portal_ciudadano_consulta_detalle, name="consulta_detalle"),
    path("consultas/<int:pk>/enviar/", portal_ciudadano_enviar_mensaje, name="enviar_mensaje"),
    path("notificaciones/turnos/leidas/", portal_ciudadano_notificaciones_turnos_leidas, name="notificaciones_turnos_leidas"),

    # Turnos
    path("turnos/", portal_ciudadano_mis_turnos, name="turnos"),
    path("turnos/solicitar/", portal_ciudadano_solicitar_turno, name="solicitar_turno"),
    path("turnos/solicitar/<int:recurso_id>/calendario/", portal_ciudadano_turno_calendario, name="turno_calendario"),
    path("turnos/solicitar/<int:recurso_id>/slots/", portal_ciudadano_turno_slots, name="turno_slots"),
    path("turnos/solicitar/disponibles-por-fecha/", portal_ciudadano_turnos_disponibles_por_fecha, name="turnos_disponibles_por_fecha"),
    path("turnos/solicitar/<int:recurso_id>/agenda/", portal_ciudadano_agenda_sede, name="agenda_sede"),
    path("turnos/solicitar/agenda-general/", portal_ciudadano_agenda_general, name="agenda_general"),
    path("turnos/solicitar/<int:recurso_id>/confirmar/", portal_ciudadano_confirmar_turno, name="confirmar_turno"),
    path("turnos/<int:pk>/confirmado/", portal_ciudadano_turno_confirmado, name="turno_confirmado"),
    path("turnos/<int:pk>/cancelar/", portal_ciudadano_cancelar_turno, name="cancelar_turno"),

    # Reclamos
    path("reclamos/", PortalCiudadanoReclamosView.as_view(), name="reclamos"),
    path("reclamos/detalle/", PortalCiudadanoReclamoDetalleView.as_view(), name="reclamos_detalle"),
    path("reclamos/confirmar/", PortalCiudadanoReclamoConfirmarView.as_view(), name="reclamos_confirmar"),
    path("reclamos/enviado/", PortalCiudadanoReclamoEnviadoView.as_view(), name="reclamos_enviado"),
    path("mis-solicitudes/reclamo/<int:pk>/", PortalCiudadanoReclamoDetalleSolicitudView.as_view(), name="detalle_reclamo"),

    # Trámites
    path("tramites/", PortalCiudadanoTramitesView.as_view(), name="tramites"),
    path("tramites/detalle/", PortalCiudadanoTramiteDetalleView.as_view(), name="tramites_detalle"),
    path("tramites/detalle/iniciar/", PortalCiudadanoTramiteInicioView.as_view(), name="tramites_detalle_iniciar"),
    path("tramites/confirmar/", PortalCiudadanoTramiteConfirmarView.as_view(), name="tramites_confirmar"),
    path("tramites/enviado/", PortalCiudadanoTramiteEnviadoView.as_view(), name="tramites_enviado"),
    path("mis-solicitudes/tramite/<int:pk>/", PortalCiudadanoTramiteDetalleSolicitudView.as_view(), name="detalle_tramite"),
]
